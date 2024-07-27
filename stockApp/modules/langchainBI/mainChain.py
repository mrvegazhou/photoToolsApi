# -*- coding: utf-8 -*-
import sys
sys.path.append("/Users/vega/workspace/codes/py_space/working/stockApi")
import re
import json
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.output_parsers.json import parse_json_markdown
from langchain.memory import ConversationBufferWindowMemory
from langchain_zhipu import ChatZhipuAI
import datetime
from configs.config import *
from core.log.logger import get_module_logger
from knowledge.sourceService import SourceService
from queryDatas.queryExecute import query_execute
from utils.structured import ResponseSchema, StructuredOutputParser
from utils.output import out_json_data

logger = get_module_logger("langchainBI-MainChain")

time_today = datetime.date.today()


class MainChain:
    llm: object = None
    service: SourceService = None
    memory: object = None
    top_k: int = LLM_TOP_K
    llm_model: str
    his_query: str

    def init_cfg(self,
                 llm_model: str = LLM_MODEL_CHAT_GLM,
                 embedding_model: str = EMBEDDING_MODEL_DEFAULT,
                 llm_history_len=LLM_HISTORY_LEN,
                 top_k=LLM_TOP_K
                 ):
        self.init_mode(llm_model, llm_history_len)
        self.service = SourceService(embedding_model, LOCAL_EMBEDDING_DEVICE)
        self.his_query = ""
        self.top_k = top_k

    def init_mode(self, llm_model: str = LLM_MODEL_CHAT_GLM, llm_history_len: str = LLM_HISTORY_LEN):
        self.llm_model = llm_model
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            max_len=50,
            return_messages=True,
            # output_key="answer",
            # chat_memory=[],
            k=llm_history_len
        )
        # self.llm = ChatZhipuAI(api_key="3e5ee7cca3201fc9985d602fc10e2399.VJyONS6cjFD4zmuV")

        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(
            openai_api_key='sk-7LB31ifIyCHK75HBfNqYnyF795d4OlmBGwoFQFc8NbQr9Fnw',
            base_url='https://api.chatanywhere.tech/v1',
            model='gpt-3.5-turbo',
            temperature=0,
        )

    def conversational_retrieval_chain(self, memory=False, invoke={}, prompt=[], input_variables=[], partial_variables={}, top_k=6, vector_path=VECTOR_STORE_PATH):
        vector_store = self.service.load_vector_store(vector_path)
        prompt = ChatPromptTemplate(
            messages=prompt,
            input_variables=input_variables,
            partial_variables=partial_variables
        )
        if memory:
            knowledge_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=vector_store.as_retriever(search_kwargs={"k": top_k}),
                combine_docs_chain_kwargs={'prompt': prompt},
                verbose=True,
                memory=self.memory,
                get_chat_history=lambda h: h,
                # output_key='result',
            )
        else:
            knowledge_chain = RetrievalQA.from_llm(
                llm=self.llm,
                retriever=vector_store.as_retriever(search_kwargs={"k": top_k}),
                prompt=prompt
            )

        try:
            return knowledge_chain.invoke(invoke)  # 只输出answer：return_only_outputs=True
        except Exception as e:
            print(e)

    def first_prompt_intent(self, query: str):
        """通过用户问题获取到完整的prompt
        """
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d")
        if current_time.hour < 15:
            formatted_time = (current_time - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        print('===============================Intent Detecting===========================================')
        sys_template = """你是智能数据分析助手，根据Human给出的提示，识别Human的意图，并完善Human的句子。"""
        system_message_prompt = SystemMessagePromptTemplate.from_template(sys_template)
        human_template = '{context}\n\n' + 'Instruction:' + '今天的日期是' + formatted_time + ', {question} ###New Instruction: '
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        vector_path = VECTOR_STORE_PATH + '/prompt_intent_detection_FAISS'
        res = self.conversational_retrieval_chain(invoke={"question": query},
                                                  prompt=[system_message_prompt, human_message_prompt],
                                                  input_variables=["context", "question"],
                                                  vector_path=vector_path,
                                                  memory=True)
        print(res, '----1----')
        return res['answer']

    def second_prompt_intent(self, query: str):
        print('===============================Task Planing===========================================')
        sys_template = """请根据给定的指令,选择最合适的task并生成其task_instruction,格式是task1={{'task_name':'task_instruction'}},可选的task有四类,包括
                        [fund_task:用于提取和处理关于所有公募基金任务, 
                        stock_task: 用于提取和处理关于所有股票价格,指数信息,公司的财务数据等任务, 
                        economic_task: 用于提取和处理关于所有中国宏观经济和货币政策等任务以及查询公司和北向资金, 
                        visualization_task: 用于一张或者多张绘制K线图,走势图或者输出统计结果]. 
                        生成task_instruction时涉及多个指标可以采用\"依次获取\",\"循环获取\"等词. 
                        时序数据一般绘制折线图,截面数据通常绘制柱状图,用以下格式输出task1={{%s:%s}},task2={{%s:%s}}. 对于预测任务只打印表格
                    """
        system_message_prompt = SystemMessagePromptTemplate.from_template(sys_template)
        human_template = '{context}\n\n' + 'Instruction:{question} ###Plan:'
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        vector_path = VECTOR_STORE_PATH + '/prompt_task_FAISS'
        res = self.conversational_retrieval_chain(invoke={"question": query},
                                                  prompt=[system_message_prompt, human_message_prompt],
                                                  input_variables=["context", "query"],
                                                  vector_path=vector_path,
                                                  memory=True)
        task_select = res['answer']
        pattern = r"(task\d+=)(\{[^}]*\})"
        matches = re.findall(pattern, task_select)
        task_plan = {}
        for task in matches:
            task_step, task_select = task
            task_select = task_select.replace("'", "\"")  # Replace single quotes with double quotes.
            task_select = json.loads(task_select)
            task_name = list(task_select.keys())[0]
            task_instruction = list(task_select.values())[0]

            task_plan[task_name] = task_instruction

        return task_plan

    def third_prompt_intent(self, query: str, task_plan: dict):
        print('===============================Tool select and using Stage===========================================')
        task_name = list(task_plan.keys())[0].split('_task')[0]
        task_instruction = list(task_plan.values())[0]
        # 加载tool lib
        with open(PROMPT_TOOL_LIBS, 'r') as f:
            tool_lib = json.load(f)
        prompt_flat = ''
        for key, value in tool_lib.items():
            prompt_flat = prompt_flat + key + '  ' + value + '\n\n'
        human_template = f"""
                          请利用给定的函数一步一步地完成Instruction,
                          每一步你只能从以下函数库中选择一个或者多个无依赖关系的函数，
                          并且为函数生成对应的参数,参数格式要严格按照函数说明,并行地生成对应多个result_i,
                          后面步骤的函数使用之前的result作为参数输入,以###结尾\n\n
                        Function Library: {prompt_flat} \n\n + Instruction : {query} ###Function Call
                        """
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        vector_path = VECTOR_STORE_PATH + '/prompt_task_FAISS'
        res = self.conversational_retrieval_chain(invoke={"question": query},
                                                  prompt=[human_message_prompt],
                                                  input_variables=["context", "query"],
                                                  vector_path=vector_path,
                                                  memory=True)




    def get_answer_template(self):
        response_schemas = [
            ResponseSchema(name="dimensions", description="实体：如股票，指数，基金，可转债等"),
            ResponseSchema(name="indicators", description="数据指标: 如市盈率，成交量等"),
            ResponseSchema(name="operator", description="计算类型: 明细，求和，最大值，最小值，平均值"),
            ResponseSchema(name="time_type", description="时间类型: 天、周、月、小时"),
            ResponseSchema(name="filters", description="过滤条件"),
            ResponseSchema(name="filter_type", description="过滤条件类型：不包括，大于，等于，小于，范围"),
            ResponseSchema(name="date_range",
                           description="日期范围,需按当前日期计算，假如当前日期为：2023-12-01，问 过去三个月或近几个月，则输出2023-09-01，2023-11-30；问过去一个月或上个月，则输出2023-11-01，2023-11-30；问八月或8月，则输出2023-08-01，2023-08-31；"),
            ResponseSchema(name="compares", description="")
        ]
        output_parser = StructuredOutputParser.set_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        return format_instructions

    def run_answer(self, query, vs_path, chat_history, top_k=VECTOR_SEARCH_TOP_K):
        result_dict = {"data": "对不起，查询失败"}
        out_dict = self.get_intent_identify(query, vs_path, top_k)
        out_str = out_dict["info"]
        print(parse_json_markdown(out_str), "----out_str---")
        if out_dict["code"] == 200:
            try:
                res_dict = parse_json_markdown(out_str)
                # 从字典中转化为数据查询语言格式
                out_json = out_json_data(res_dict)
            except Exception as e:
                logger.error(e)
                return out_str, chat_history
        else:
            result_dict["data"] = out_str
            return result_dict, chat_history
        # try:
        #     res_dict = parse_json_markdown(out_str)
        #     # 从字典中转化为数据查询语言格式
        #     out_json = out_json_data(res_dict)
        #     print(out_json, "----out_json---")
        #     result_dict["data"] = str(query_execute(out_json))
        # except Exception as e:
        #     logger.error(e)
        #     return result_dict, chat_history

    def get_intent_identify(self, query: str, vs_path: str = VECTOR_STORE_PATH, top_k=VECTOR_SEARCH_TOP_K):
        out_dict = {"code": 500}

        template = """ 你是股票数据分析专家，根据上下文和Human提问，识别对方数据分析意图('完整'、'缺失'、'闲聊')
                        ## 背景知识
                        完整：
                            1.提问信息中需包含指数或股票或公司，同时包含指标，没指定时间范围则用今天代替，例如：东方财富的开盘价是多少，为完整。
                            2.提问信息只包含实体，例如：东方财富，为完整。
                            3.提问信息只包含技术指标和条件，为完整，例如：macd零轴金叉，为完整。
                        缺失：
                            1.提问中包含股票基金等实体，但指标并非实体的属性，为缺失，例如：东方财富的水分是多少？
                            2.提问中有实体，但是没有指标和条件，例如：东方财富今天是多少？
                        闲聊：跟股票数据查询无关，如：天气如何
    
                        ## 回答约束
                        先根据上下文分析意图是否完整，如完整，从问题中抽取json结构的信息。
                        如果不满足意图完整，返回空集合。
                        json字段包括：{{format_instructions}}
                        当前日期：{time_today}，
                        已知内容：{{context}}。
                        若意图缺失，提示和股票问题无关，无法回答。
                        若意图为闲聊，需要提示应该提问股票数据问题，禁止出现大模型名称或公司的提示。
    
                        ## 输出格式
                        如意图完整，去掉备注，返回json集合。
                        如意图缺失或闲聊，返回字符串。
                        
                        {{chat_history}}
                    """
        format_instructions = self.get_answer_template()
        system_message_prompt = SystemMessagePromptTemplate.from_template(template.format(time_today=time_today))

        human_template = "{question}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        prompt = ChatPromptTemplate(
            messages=[
                system_message_prompt, human_message_prompt
            ],
            input_variables=["chat_history", "context", "question"],
            partial_variables={"format_instructions": format_instructions}
        )

        vector_store = self.service.load_vector_store(vs_path)
        knowledge_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vector_store.as_retriever(search_kwargs={"k": top_k}),
            # chain_type='stuff',
            # return_source_documents=True,
            combine_docs_chain_kwargs={'prompt': prompt},
            verbose=True,
            memory=self.memory,
            get_chat_history=lambda h: h,
            # output_key='result',
            # condense_question_llm=ChatOpenAI(temperature=0, model='gpt-3.5-turbo'),
        )

        try:
            res = knowledge_chain.invoke({"question": query})  # 只输出answer：return_only_outputs=True
            out_dict["code"] = 200
            out_dict["info"] = res['answer']
            self.memory.save_context({"input": query}, {"output": res['answer']})
        except Exception as e:
            print(e)
            out_dict["info"] = "sorry，LLM model (%s) is fail，wait a minute..." % self.llm_model
        return out_dict


if __name__ == "__main__":
    prompt_path = 'prompt_lib.txt'
    def set_vector_store(chain):
        vs_path = chain.service.init_knowledge_vector_store([prompt_path])


    import os
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    chain = MainChain()

    chain.init_cfg(llm_model='xxx',
                   embedding_model=EMBEDDING_MODEL_DEFAULT,
                   llm_history_len=5,
                   top_k=3)
    set_vector_store(chain)
    xxx
    query = "东方财富的成交量"
    # history = [[query, None]]
    # vs_path = '/Users/vega/workspace/codes/py_space/案例/股票/Langchain-ChatBI/vector_store/knowledge/content/question_answer_FAISS_20240725_234029'
    # chain.run_answer(query=query, vs_path=vs_path, chat_history=history, top_k=3)

    answer = chain.first_prompt_intent(query)
    res = chain.second_prompt_intent(answer)
    print(res)