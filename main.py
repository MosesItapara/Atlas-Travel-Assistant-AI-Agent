from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
from atlas_engine import AtlasEngine, build_vectorstore
from dotenv import load_dotenv
import uuid
import os
import traceback

load_dotenv()

##LIFESPAN

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Atlas is starting up...")
    app.state.vectorstore = build_vectorstore()

    app.state.sessions = {}

    print("✅ Atlas is ready to handle requests!")
    yield
    print("👋 Atlas shutting down...")

    ## APP

app = FastAPI(
    title="Atlas Travel Assistant",
    description="AI-powered travel planning API",
    version="1.0.0",
    lifespan=lifespan
    )

    # CORS allows frontend to talk to the API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    )

    # Serve HTML, CSS, JS files from /static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

    # REQUEST/ RESPONSE MODELS
    #Pydantic validates incoming JSON

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str

    # ROUTES

@app.get("/")
async def serve_frontend():
    """Serve the main chat UI."""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """
    Health check - Render and UptimeRobot ping this.
    Returns 200 OK if server is alive.
    """

    return {
        "status": "healthy",
        "assistant": "Atlas",
        "sessions_active": len(app.state.sessions)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Flow:
    1. Receive {message, session_id} from frontend
    2. Create new session if session_id is new/missing
    3. Pass message to AtlasEngine
    4. Return {reply, session_id}
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())

        if session_id not in app.state.sessions:
            app.state.sessions[session_id] = AtlasEngine(
                app.state.vectorstore
            )
        
        engine = app.state.sessions[session_id]
        reply = engine.chat(request.message)

        return ChatResponse(reply=reply, session_id=session_id)
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a user's memory.
    Called when user clicks 'New Chat' button.
    """

    if session_id in app.state.sessions:
        app.state.sessions[session_id].clear_memory()
        del app.state.sessions[session_id]
        return {"message": "Session cleared successfully"}
    raise HTTPException(status_code=404, detail="Session not found")
    


 