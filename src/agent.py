import os
import sys

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
import openai
from colorama import Fore, Style
from dotenv import load_dotenv
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import Settings
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import FunctionTool
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

from .common import setup_logger, write
from .consts import DATA_DIR, CHROMA_DB_PATH, SYSTEM_AGENT_X, SYSTEM_AGENT_Y, TOOL_DESCRIPTION

logger = setup_logger()

# Load environment variables
load_dotenv()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")
openai.api_key = os.getenv("API_KEY")

# Configure OpenAI settings
Settings.chunk_size = 512
Settings.chunk_overlap = 64
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.text_splitter = MarkdownNodeParser()

# Initialize OpenAI language models
llm_agentX = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
llm_agentY = OpenAI(temperature=0.1, model="gpt-4")


def load_and_index() -> VectorStoreIndex:
    """Load and index data from ChromaDB. If the index is not found, index the data and save it to ChromaDB."""
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


def send_email(name: str, email: str) -> bool:
    """This is mock function to send email to the user. Return True if email is sent successfully."""
    if name and email:
        return True
    return False


def chat_engine(verbose: bool = False) -> dict[str, OpenAIAgent]:
    """Create and return agents for the chat engine."""
    index = load_and_index()

    # Create tools for the agents
    query_tool = QueryEngineTool(
        query_engine=index.as_query_engine(),
        metadata=ToolMetadata(
            name=f"car_details_and_information_provider_tool",
            description=TOOL_DESCRIPTION,
        )
    )

    send_email_tool = FunctionTool.from_defaults(fn=send_email)
    query_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=[query_tool])

    query_engine_tool = QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="car_details_and_information_provider",
            description=TOOL_DESCRIPTION,
        )
    )

    # Add custom chat history for agentX So it can begin with context
    custom_chat_history = [
        ChatMessage(
            role=MessageRole.ASSISTANT,
            content="Hello, How can I help you selecting car. Can you let me know the "
                    "preference of car you are looking for?",
        ),
    ]

    # Create agents
    agentX = OpenAIAgent.from_tools([query_engine_tool],
                                    system_prompt=SYSTEM_AGENT_X,
                                    chat_history=custom_chat_history,
                                    llm=llm_agentX,
                                    verbose=verbose
                                    )

    agentY = OpenAIAgent.from_tools([query_engine_tool, send_email_tool],
                                    system_prompt=SYSTEM_AGENT_Y,
                                    llm=llm_agentY,
                                    verbose=verbose
                                    )

    agents = {
        "agentX": agentX,
        "agentY": agentY
    }

    return agents


def repl_chat() -> None:
    """Start the chat engine in REPL mode."""
    agents = chat_engine(verbose=False)
    write(f"Hello, How can I help you selecting car. Can you let me know "
          f"the preference of car you are looking for?",
          role="assistant")

    passed = 0  # Flag to check if user has passed to agentY
    while True:
        prompt = input(f"{Fore.WHITE}You > {Style.RESET_ALL}")

        if passed == 0:
            response = agents["agentX"].chat(prompt)
        else:
            response = agents["agentY"].chat(prompt)

        if prompt == "exit":
            sys.exit(0)

        if "</EXIT>" in str(response):
            write(
                f"Agent (Y): Thank you for your time. Your car has been booked. \
                We will send you an email with the details.",
                role="assistant")
            sys.exit(0)

        # Check if user has passed to agentY, and if so, check for the </PASS> token
        if "</PASS>" in str(response) or "<PASS>" in str(response):
            write(f"Hello I am agent Y. I am here to help you with purchase. May I know your name?", role="assistant",
                  agent="Y")
            agents["agentY"].chat_history.append(agents["agentX"].chat_history[-3])
            agents["agentY"].chat_history.append(agents["agentX"].chat_history[-2])
            agents["agentY"].chat_history.append(agents["agentX"].chat_history[-1])
            passed = 1
            continue

        if passed == 0:
            write(f"{response}", role="assistant")
        else:
            write(f"{response}", role="assistant", agent="Y")
