import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Student Assistant")
st.caption("MCP + SQLite + RAG + Guardrails")


# ============================================================
# GUARDRAILS
# ============================================================

def input_guardrail(user_input):

    blocked_words = [
        "password",
        "credit card",
        "bank account"
    ]

    text = user_input.lower()

    for word in blocked_words:
        if word in text:
            return False

    return True


def output_guardrail(answer):

    if not answer or not answer.strip():
        return "I could not find enough information to answer your question."

    return answer


# ============================================================
# LLM
# ============================================================

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)


# ============================================================
# MCP
# ============================================================

mcp_client = MultiServerMCPClient({

    "student_database": {

        "command": "python",

        "args": [
            "mcp_server.py"
        ],

        "transport": "stdio"
    }
})


# ============================================================
# INITIALIZE AGENT
# ============================================================

async def initialize_agent():

    tools = await mcp_client.get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,

        system_prompt="""
        You are a helpful AI student assistant.

        Use MCP for student database questions.

        Use the provided PDF context for document questions.

        Never invent information.

        Student fields:
        Name, Age, Course, City.
        """
    )

    return agent


# ============================================================
# CREATE AGENT
# ============================================================

if "agent" not in st.session_state:

    st.session_state.agent = asyncio.run(
        initialize_agent()
    )


# ============================================================
# CHAT HISTORY
# ============================================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


# ============================================================
# PDF PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PDF_PATH = os.path.join(
    BASE_DIR,
    "documents",
    "students.pdf"
)


# ============================================================
# CREATE VECTOR DATABASE
# ============================================================

@st.cache_resource
def create_vector_database():

    documents = PyPDFLoader(
        PDF_PATH
    ).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(
        documents
    )

    embeddings = OpenAIEmbeddings()

    vector_db = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_db


# ============================================================
# LOAD VECTOR DATABASE
# ============================================================

vector_db = create_vector_database()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.chat_history:

    if isinstance(message, HumanMessage):

        with st.chat_message("user"):
            st.write(message.content)

    else:

        with st.chat_message("assistant"):
            st.write(message.content)


# ============================================================
# USER INPUT
# ============================================================

user_input = st.chat_input(
    "Ask about students or the PDF..."
)


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if user_input:

    # --------------------------------------------------------
    # DISPLAY USER QUESTION
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.write(user_input)


    # --------------------------------------------------------
    # INPUT GUARDRAIL
    # --------------------------------------------------------

    if not input_guardrail(user_input):

        st.warning(
            "⚠️ I can't provide sensitive information."
        )

        st.stop()


    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    st.session_state.chat_history.append(
        HumanMessage(
            content=user_input
        )
    )


    # --------------------------------------------------------
    # RAG RETRIEVAL
    # --------------------------------------------------------

    documents = vector_db.similarity_search(
        user_input,
        k=3
    )


    # --------------------------------------------------------
    # EXTRACT CONTEXT
    # --------------------------------------------------------

    contexts = [
        document.page_content
        for document in documents
    ]

    pdf_context = "\n\n".join(
        contexts
    )


    # --------------------------------------------------------
    # CREATE AGENT MESSAGE
    # --------------------------------------------------------

    message = f"""

    User question:
    {user_input}

    Relevant PDF information:
    {pdf_context}

    Instructions:

    1. Use PDF information when relevant.
    2. Use MCP for student database questions.
    3. Do not invent information.
    4. If the information is not available, say so.
    """


    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = asyncio.run(
                st.session_state.agent.ainvoke(
                    {
                        "messages": [
                            HumanMessage(
                                content=message
                            )
                        ]
                    }
                )
            )


            # ------------------------------------------------
            # GET ANSWER
            # ------------------------------------------------

            answer = response[
                "messages"
            ][-1].content


            # ------------------------------------------------
            # OUTPUT GUARDRAIL
            # ------------------------------------------------

            answer = output_guardrail(
                answer
            )


            # ------------------------------------------------
            # DISPLAY ANSWER
            # ------------------------------------------------

            st.write(answer)


    # --------------------------------------------------------
    # SAVE AI MESSAGE
    # --------------------------------------------------------

    st.session_state.chat_history.append(
        AIMessage(
            content=answer
        )
    )