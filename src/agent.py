import os

import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

from .common import setup_logger
from .consts import DATA_DIR, CHROMA_DB_PATH
import openai

logger = setup_logger()

Settings.chunk_size = 512
Settings.chunk_overlap = 64
Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")
openai.api_key = os.getenv("API_KEY")


def load_and_index():
    # Save and load from ChromaDB
    if os.path.exists(CHROMA_DB_PATH):
        logger.info("Loading index from ChromaDB")

        db = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        chroma_collection = db.get_or_create_collection("car_collection")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store)

    else:
        logger.info("Indexing data and saving to ChromaDB")

        docs = SimpleDirectoryReader(input_dir=DATA_DIR).load_data()
        db = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        chroma_collection = db.get_or_create_collection("car_collection")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)

    return index

# def chat_engine(verbose: bool = False) -> OpenAIAgent:
#     available_doctors_tool_conversational = FunctionTool.from_defaults(fn=get_doctor_name_by_speciality)
#     get_doctors_specialities_tool = FunctionTool.from_defaults(fn=get_available_doctors_specialities)

#     custom_chat_history = [
#         ChatMessage(
#             role=MessageRole.ASSISTANT,
#             content="Hello, I am your personal medical assistant. How are you feeling today?",
#         ),
#     ]

#     agent = OpenAIAgent.from_tools([available_doctors_tool_conversational, get_doctors_specialities_tool],
#                                    system_prompt=SYSTEM_AGENT_SIMPLE,
#                                    chat_history=custom_chat_history,
#                                    verbose=verbose)
#     return agent
