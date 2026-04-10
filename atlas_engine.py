# atlas_engine.py — Core AI Logic

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool
from knowledge_base import TRAVEL_KNOWLEDGE
from dotenv import load_dotenv
import requests
import os

load_dotenv()


# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────

@tool
def get_weather(city: str) -> str:
    """
    Get current weather for any city.
    Use this whenever the user asks about weather,
    climate, or what to expect temperature-wise at a destination.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("cod") != 200:
            return f"Could not find weather for {city}. Check the city name."

        temp        = data["main"]["temp"]
        feels_like  = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity    = data["main"]["humidity"]
        wind        = data["wind"]["speed"]

        return (
            f"Weather in {city}: {description.capitalize()}, "
            f"{temp}°C (feels like {feels_like}°C), "
            f"Humidity: {humidity}%, Wind: {wind} m/s"
        )
    except requests.Timeout:
        return "Weather request timed out. Please try again."
    except Exception as e:
        return f"Weather lookup failed: {str(e)}"


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert an amount from one currency to another.
    Use this when the user asks about costs, budgets,
    how much something costs in local currency,
    or any currency conversion question.
    Example inputs: amount=100, from_currency='USD', to_currency='KES'
    """
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    url = (
        f"https://v6.exchangerate-api.com/v6/{api_key}"
        f"/pair/{from_currency}/{to_currency}/{amount}"
    )
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # ✅ Fixed: was data.get("results") — correct key is "result"
        if data.get("result") != "success":
            return f"Could not convert {from_currency} to {to_currency}."

        converted = data["conversion_result"]
        rate      = data["conversion_rate"]

        return (
            f"{amount} {from_currency} = {converted:.2f} {to_currency} "
            f"(Rate: 1 {from_currency} = {rate} {to_currency})"
        )
    except requests.Timeout:
        return "Currency request timed out. Please try again."
    except Exception as e:
        return f"Currency conversion failed: {str(e)}"


# ─────────────────────────────────────────────
# VECTOR STORE
# ─────────────────────────────────────────────

def build_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if os.path.exists("./atlas_knowledge"):
        print("📂 Loading existing vector store from disk...")
        return Chroma(
            persist_directory="./atlas_knowledge",
            embedding_function=embeddings
        )

    print("🔨 Building vector store for first time...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(TRAVEL_KNOWLEDGE)
    print(f"✅ Created {len(chunks)} chunks from knowledge base")

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="./atlas_knowledge"
    )

    print("✅ Vector store saved to disk!")
    return vectorstore


# ─────────────────────────────────────────────
# ATLAS ENGINE CLASS
# ─────────────────────────────────────────────

class AtlasEngine:
    def __init__(self, vectorstore):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # ✅ New prompt replacing deprecated ConversationalRetrievalChain
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Atlas, an expert AI travel assistant.
Use the following context to answer travel questions accurately.
Context: {context}
Be friendly, concise and enthusiastic about travel!"""),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        # ✅ New chain replacing deprecated ConversationalRetrievalChain
        combine_chain = create_stuff_documents_chain(self.llm, prompt)
        self.chain = create_retrieval_chain(
            vectorstore.as_retriever(search_kwargs={"k": 3}),
            combine_chain
        )

        # ✅ Manual history replacing deprecated ConversationBufferMemory
        self.chat_history = []

    def chat(self, user_message: str) -> str:
        """Process a message and return Atlas's reply."""
        response = self.chain.invoke({
            "input": user_message,
            "chat_history": self.chat_history
        })

        # Save to history for next turn
        self.chat_history.append(HumanMessage(content=user_message))
        self.chat_history.append(AIMessage(content=response["answer"]))

        return response["answer"]

    def clear_memory(self):
        """Wipe conversation history for this session."""
        self.chat_history = []