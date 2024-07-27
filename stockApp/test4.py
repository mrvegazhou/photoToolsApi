
from langchain import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_zhipu import ChatZhipuAI
from langchain.prompts.prompt import PromptTemplate
import os


def test1():
    db = SQLDatabase.from_uri("sqlite:////Users/vega/workspace/codes/py_space/案例/股票/DB-GPT/pilot/data/default_sqlite.db")
    # api_key = os.getenv("OPENAI_API_KEY", "sk-7LB31ifIyCHK75HBfNqYnyF795d4OlmBGwoFQFc8NbQr9Fnw")
    # base_urls = ["https://api.chatanywhere.tech/v1", "https://api.chatanywhere.com.cn/v1"]
    # llm = OpenAI(temperature=0, verbose=True, api_key=api_key, base_url=base_urls[0])
    # llm = OpenAI(model_name="gpt-3.5-turbo-instruct", http_client=httpx.Client(proxies="http://proxy.yourcompany.com:8080"))
    llm = ChatZhipuAI(api_key="3e5ee7cca3201fc9985d602fc10e2399.VJyONS6cjFD4zmuV")

    _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Use the following format:

    Question: "Question here"
    SQLQuery: "SQL Query to run"
    SQLResult: "Result of the SQLQuery"
    Answer: "Final answer here"

    Only use the following tables:

    {table_info}

    If someone asks for the table foobar, they really mean the employee table.

    Question: {input}"""
    PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
    )

    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
    db_chain.run("How many students are there?")



from langchain_core.tools import tool


@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int


@tool
def add(first_int: int, second_int: int) -> int:
    "Add two integers."
    return first_int + second_int


@tool
def exponentiate(base: int, exponent: int) -> int:
    "Exponentiate the base to the exponent power."
    return base ** exponent





if __name__ == '__main__':
    # from langchain import hub
    # from langchain.agents import create_structured_chat_agent
    # from langchain.agents import AgentExecutor
    #
    # tools = [multiply, add, exponentiate]
    # prompt = hub.pull("hwchase17/structured-chat-agent")
    #
    # llm = ChatZhipuAI(api_key="3e5ee7cca3201fc9985d602fc10e2399.VJyONS6cjFD4zmuV")
    #
    # agent = create_structured_chat_agent(llm, tools, prompt)
    # agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True)
    #
    # agent_executor.invoke(
    #     {
    #         "input": "Take 3 to the fifth power and multiply that by the sum of twelve and three, then square the whole result"
    #     }
    # )

    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.chains import LLMChain

    # 导入所需库和模块
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.chains import LLMChain

    # 使用Pydantic创建数据格式
    from pydantic import BaseModel, Field
    from typing import List


    class Flower(BaseModel):
        name: str = Field(description="name of a flower")
        colors: List[str] = Field(description="the colors of this flower")


    # 创建提示模板实例
    template = "{flower}的花语是？"
    llm = ChatOpenAI(
        openai_api_key='sk-7LB31ifIyCHK75HBfNqYnyF795d4OlmBGwoFQFc8NbQr9Fnw',
        base_url='https://api.chatanywhere.tech/v1',
        model='gpt-3.5-turbo',
        temperature=0,
    )
    prompt = PromptTemplate.from_template(template)

    # 初始化LLMChain
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )

    # 调用LLMChain并获取结果
    result = llm_chain.invoke("玫瑰")
    print(result)




