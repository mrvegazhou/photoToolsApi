import torch.cuda
import torch.backends
from stockApp.config import mainConst

APP_BOOT_PATH = '/Users/vega/workspace/codes/py_space/working/stockApi/stockApp/modules/langchainBI' #mainConst.APP_BOOT_PATH
MODEL_BOOT_PATH = APP_BOOT_PATH + "/llm/models"

VECTOR_SEARCH_TOP_K = 10
LLM_TOP_K = 6
LLM_HISTORY_LEN = 8
LLM_MODEL_CHAT_GLM = "glm-4-air"
LLM_OPEN_AI = "gpt-3.5-turbo"

EMBEDDING_MODEL_DEFAULT = "bge-large-zh"
LOCAL_EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
# 多模型选择，向量模型选择
embedding_model_dict = {
    "bge-large-zh": MODEL_BOOT_PATH + "/bge-large-zh-v1.5",
    "text2vec": MODEL_BOOT_PATH + "/text2vec-large-chinese",
}
VECTOR_PROMPT_PATH = APP_BOOT_PATH + "/llm/vectorStore/prompts"
VECTOR_STORE_PATH = APP_BOOT_PATH + "/llm/vectorStore/knowledge"
PROMPT_TOOL_LIBS = APP_BOOT_PATH + "/llm/datas/tool_stock.json"