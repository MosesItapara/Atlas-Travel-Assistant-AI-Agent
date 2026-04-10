<div align="center">

# ✈️ Atlas — AI Travel Assistant

**Your personal AI-powered travel guide. Ask anything. Go anywhere.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-orange?style=for-the-badge)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-purple?style=for-the-badge)](https://groq.com)
[![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)

<br/>

![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge)

<br/>

> *Built in 5 days as a structured deep-dive into LLMs, LangChain, RAG, and FastAPI deployment.*

</div>

---

## 🌍 What is Atlas?

Atlas is a full-stack AI travel assistant that goes beyond a basic chatbot. It combines **Retrieval-Augmented Generation (RAG)**, **live tool calling**, and **persistent memory** to give you genuinely useful travel advice — not just generic LLM responses.

Ask it about destinations, visa requirements, packing tips, live weather, currency conversion, or trip budgets. It remembers your conversation and searches its own knowledge base before answering.

---

## ⚡ Features

| Feature | Description |
|---------|-------------|
| 🧠 **RAG Knowledge Base** | Searches curated travel knowledge via ChromaDB before every response |
| 🌤️ **Live Weather** | Fetches real-time weather for any city via OpenWeather API |
| 💱 **Currency Conversion** | Live exchange rates for any currency pair |
| 💬 **Conversation Memory** | Remembers context across your entire session |
| 👥 **Multi-user Sessions** | Each user gets isolated memory — no conversations mixing |
| 🚀 **Fast Inference** | Powered by Groq — one of the fastest LLM inference providers |
| 🎨 **Clean Chat UI** | No frameworks — pure HTML, CSS, JS with a polished dark theme |

---

## 🛠️ Tech Stack

```
🤖  LLM              Groq — LLaMA 3.3 70B Versatile
🔗  Framework        LangChain — chains, retrieval, tool calling
🗄️  Vector Store     ChromaDB — local semantic search
🔢  Embeddings       HuggingFace sentence-transformers/all-MiniLM-L6-v2
⚡  API Server       FastAPI + Uvicorn
🎨  Frontend         Vanilla HTML / CSS / JavaScript
☁️  Deployment       Railway
```

---

## 🏗️ Architecture

```
Browser (Chat UI)
      │
      │  POST /chat
      ▼
FastAPI Server (main.py)
      │
      │  routes to user session
      ▼
Atlas Engine (atlas_engine.py)
      │
      ├──► ChromaDB Vector Store
      │         searches top 3 relevant chunks
      │
      ├──► Tools (if needed)
      │         get_weather("Nairobi")
      │         convert_currency(100, "USD", "KES")
      │
      └──► Groq LLM (LLaMA 3.3 70B)
                combines chunks + tools + history
                      │
                      ▼
               Final Response → User
```

---

## 📁 Project Structure

```
atlas-travel-assistant/
│
├── 📄 main.py                # FastAPI server — routes & session management
├── 🤖 atlas_engine.py        # Core AI logic — RAG chain, tools, memory
├── 📚 knowledge_base.py      # Curated travel knowledge text
│
├── 🌐 static/
│   └── index.html            # Chat UI (HTML + CSS + JS)
│
├── 📋 requirements.txt       # Python dependencies
├── 🚂 railway.json           # Railway deployment config
├── 🐍 runtime.txt            # Python version pin
└── 🔒 .env                   # API keys (never committed)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Git
- API keys for Groq, OpenWeather, and ExchangeRate (all free)

### 1. Clone the repository

```bash
git clone https://github.com/MosesItapara/Atlas-Travel-Assistant-AI-Agent.git
cd Atlas-Travel-Assistant-AI-Agent
```

### 2. Set up virtual environment

```bash
# Create venv
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt --timeout 300
```

### 4. Configure environment variables

Create a `.env` file in the root folder:

```env
GROQ_API_KEY=your_groq_key_here
OPENWEATHER_API_KEY=your_openweather_key_here
EXCHANGERATE_API_KEY=your_exchangerate_key_here
```

<details>
<summary>📌 Where to get free API keys</summary>

| API | Link | Free Tier |
|-----|------|-----------|
| Groq | https://console.groq.com | Generous free limits |
| OpenWeather | https://openweathermap.org/api | 1,000 calls/day |
| ExchangeRate | https://www.exchangerate-api.com | 1,500 calls/month |

> ⚠️ OpenWeather keys take 10–30 minutes to activate after signup.

</details>

### 5. Run the server

```bash
uvicorn main:app --reload --port 8000
```

### 6. Open in your browser

```
http://localhost:8000        → Chat UI
http://localhost:8000/docs   → API documentation
http://localhost:8000/health → Health check
```

---

## 🧠 How RAG Works in Atlas

RAG (Retrieval-Augmented Generation) means Atlas doesn't just rely on what the LLM already knows. It actively searches its own knowledge base first.

```
Your question: "Best time to visit Nairobi?"
        │
        ▼
Question gets embedded → [0.45, 0.23, 0.91, ...]
        │
        ▼
ChromaDB finds 3 closest chunks from knowledge base:
   → "KENYA - NAIROBI" chunk ✅
   → "TRAVEL TIPS - PACKING" chunk ✅
   → "TRAVEL TIPS - BUDGETING" chunk ✅
        │
        ▼
LLM receives: chunks + your question + chat history
        │
        ▼
Atlas: "The best time to visit Nairobi is July to October
        for wildlife viewing in Maasai Mara..."
```

This grounds the AI's responses in real, curated information rather than hallucination.

---

## 🔧 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the chat UI |
| `GET` | `/health` | Server health check |
| `POST` | `/chat` | Send a message, receive a reply |
| `DELETE` | `/session/{id}` | Clear conversation history |

### Example request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Nairobi?", "session_id": null}'
```

### Example response

```json
{
  "reply": "Currently in Nairobi: Clear sky, 22°C (feels like 20°C), Humidity: 61%, Wind: 3.2 m/s — perfect weather for a safari! 🌍",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 📅 5-Day Build Journey

This project was built as a structured 5-day challenge to go from zero to a deployed AI application.

<details>
<summary>See the full breakdown</summary>

**Day 1 — Foundations**  
Set up the Groq API client, understood how conversation history works, built a basic terminal chatbot with streaming support.

**Day 2 — Travel Assistant Core Logic**  
Designed the system prompt for Atlas, refined the personality and response style, tested edge cases.

**Day 3 — LangChain + Tool Calling**  
Migrated from raw API calls to LangChain, built the weather and currency tools, learned how agents decide when to call tools.

**Day 4 — Memory + RAG**  
Built the ChromaDB vector store, implemented text splitting and embeddings, wired up the retrieval chain so Atlas could search its knowledge base.

**Day 5 — Web Interface + Deployment**  
Built the FastAPI server with session management, designed the chat UI from scratch, pushed to GitHub, and deployed on Railway.

</details>

---

## 🤔 Challenges & Lessons

The biggest lessons from building this:

- **LangChain moves fast** — several APIs deprecated between versions. Always check the latest docs.
- **Memory management matters** — getting per-user session isolation right took careful thought.
- **Free tiers have real limits** — Render's 512MB RAM couldn't handle the HuggingFace model at startup. Railway's more generous limits solved it.
- **RAG is powerful but needs good chunks** — chunk size and overlap significantly affect answer quality.

---

## 🔮 Future Improvements

- [ ] Load knowledge base from uploaded PDFs
- [ ] Add flight search tool
- [ ] Persist sessions to a database (currently in-memory)
- [ ] Add user authentication
- [ ] Support voice input
- [ ] Multi-language support

---

## 📄 License

MIT License — feel free to fork, modify, and build on this project.

---

<div align="center">

Built with ❤️ and a lot of debugging

**[⭐ Star this repo](https://github.com/MosesItapara/Atlas-Travel-Assistant-AI-Agent)** if you found it useful!

</div>
