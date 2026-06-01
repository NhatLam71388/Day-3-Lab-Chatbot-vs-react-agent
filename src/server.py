import os
import sys
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.agent import ReActAgent
from src.agent.chatbot import ChatbotBaseline
from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.tools import ALL_TOOLS

# Load environment variables
load_dotenv()

app = FastAPI(title="E-commerce Chatbot vs ReAct Agent")

# Mount static and templates folders
# Note: These folders are under src/static and src/templates
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

# Ensure directories exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

class ChatRequest(BaseModel):
    message: str
    provider: str  # "openai" | "google" | "local"
    model: str     # model name (e.g. "gpt-4o", "gemini-1.5-flash", or path to local model)
    mode: str      # "agent" | "chatbot"
    api_key: Optional[str] = None

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    provider_name = payload.provider.lower()
    model_name = payload.model.strip()
    mode = payload.mode.lower()

    # Step 1: Initialize LLM Provider based on user choice
    try:
        if provider_name == "openai":
            api_key = payload.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your_openai_api_key_here":
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Missing API Key",
                        "message": "OpenAI API Key is missing. Please set it in your .env file or enter it in the UI."
                    }
                )
            llm = OpenAIProvider(model_name=model_name, api_key=api_key)
            
        elif provider_name in ["google", "gemini"]:
            api_key = payload.api_key or os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Missing API Key",
                        "message": "Gemini API Key is missing. Please set it in your .env file or enter it in the UI."
                    }
                )
            llm = GeminiProvider(model_name=model_name, api_key=api_key)
            
        elif provider_name == "local":
            # For local models, check if file exists
            model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
            if not os.path.exists(model_path):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Model Not Found",
                        "message": f"Local model file not found at '{model_path}'. Please check LOCAL_MODEL_PATH in .env or download the Phi-3 GGUF model."
                    }
                )
            llm = LocalProvider(model_path=model_path)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider_name}")

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Initialization Error",
                "message": f"Failed to initialize LLM provider: {str(e)}"
            }
        )

    # Step 2: Initialize Agent or Chatbot and generate response
    try:
        if mode == "agent":
            agent = ReActAgent(llm=llm, tools=ALL_TOOLS)
            result = agent.run(payload.message)
        elif mode == "chatbot":
            chatbot = ChatbotBaseline(llm=llm)
            result = chatbot.run(payload.message)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported execution mode: {mode}")

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": "Execution Error",
                "message": f"Error running chatbot/agent logic: {str(e)}"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
