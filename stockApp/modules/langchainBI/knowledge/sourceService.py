
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import CSVLoader
import sentence_transformers
from typing import List
import os
import datetime
from core.log.logger import get_module_logger
from stockApp.modules.langchainBI.configs.config import *

logger = get_module_logger("langchainBI-SourceService")


class SourceService:
    """
      知识库向量化服务
    """

    def __init__(self,
                 embedding_model: str = EMBEDDING_MODEL_DEFAULT,
                 embedding_device=LOCAL_EMBEDDING_DEVICE):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model], )
        self.embeddings.client = sentence_transformers.SentenceTransformer(self.embeddings.model_name,
                                                                           device=embedding_device)
        self.vector_store = None
        self.vector_store_path = VECTOR_STORE_PATH

    def init_source_vector(self, docs_path):
        """初始化本地知识库向量

        Parameters
        ----------

        Returns
        ----------
        """
        docs = []
        for doc in os.listdir(docs_path):
            if doc.endswith('.txt'):
                loader = UnstructuredFileLoader(f'{docs_path}/{doc}', mode="elements")
                doc = loader.load()
                docs.extend(doc)
        self.vector_store = FAISS.from_documents(docs, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)

    def init_knowledge_vector_store(self, filepath: str or List[str]):
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                logger.error("路径不存在")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    loader = UnstructuredFileLoader(filepath, mode="elements")
                    docs = loader.load()
                    logger.info(f"{file} 已成功加载")
                except Exception as e:
                    logger.error(f"{file} 未能成功加载", e)
                    return None
            elif os.path.isdir(filepath):
                docs = []
                for file in os.listdir(filepath):
                    fullfilepath = os.path.join(filepath, file)
                    try:
                        loader = UnstructuredFileLoader(fullfilepath, mode="elements")
                        docs += loader.load()
                        logger.info(f"{file} 已成功加载")
                    except Exception as e:
                        logger.error(f"{file} 未能成功加载", e)
        else:
            docs = []
            for file in filepath:
                try:
                    loader = UnstructuredFileLoader(f"""{VECTOR_PROMPT_PATH}/{file}""", mode="elements")
                    docs += loader.load()
                    logger.info(f"{file} 已成功加载")
                except Exception as e:
                    logger.error(f"{file} 未能成功加载", e)

        vector_store = FAISS.from_documents(docs, self.embeddings)
        vs_path = f"""{VECTOR_STORE_PATH}/{os.path.splitext(file)[0]}_FAISS"""
        print(vs_path, "====vs_path====")
        vector_store.save_local(vs_path)
        return vs_path if len(docs) > 0 else None

    def add_document(self, document_path):
        loader = UnstructuredFileLoader(document_path, mode="elements")
        doc = loader.load()
        self.vector_store.add_documents(doc)
        self.vector_store.save_local(self.vector_store_path)

    def load_vector_store(self, path):
        if path is None:
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings,
                                                 allow_dangerous_deserialization=True)
        else:
            self.vector_store = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        return self.vector_store

    def add_csv(self, document_path):
        loader = CSVLoader(file_path=document_path)
        doc = loader.load()
        logger.info("doc:", doc)