import time
from uuid import uuid4
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Core ---
from core.router import Router
from core.schemas import ChatRequest, ChatResponse

# --- Infra ---
from infra.logging import setup_logging
from infra.settings import (
    TITLE,
    VERSION,
    MAX_BODY_BYTES,
    ENABLE_RAG,
    OFFLINE_BACKEND,
    MAX_CONCURRENT_REQUESTS,
)
from infra.preflight import verify_models
from infra.runtime import shutdown_event
from infra.metrics import metrics

# --- Security ---
from security.auth import require_api_key

# --- Models / Memory ---
from models.registry import list_profiles, get_profile
from memory.sqlite_store import SQLiteMemoryStore


# --------------------------------------------------
# Startup
# --------------------------------------------------

load_dotenv()
setup_logging()

router = Router()
api_router = APIRouter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    shutdown_event.set()
    time.sleep(0.5)


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title=TITLE,
    version=VERSION,
    lifespan=lifespan,
)


# --------------------------------------------------
# Metrics bootstrap
# --------------------------------------------------

offline_limit = 1 if OFFLINE_BACKEND == "embedded" else MAX_CONCURRENT_REQUESTS
metrics.set("offline_concurrency_limit", offline_limit)
metrics.set("offline_backend_mode", 1 if OFFLINE_BACKEND == "embedded" else 2)


# --------------------------------------------------
# API ROUTES (user-facing)
# --------------------------------------------------

@api_router.get("/models")
def list_models():
    """
    Returns available model profiles for UI / clients.
    """
    profiles = list_profiles()
    return [
        {
            "id": p.id,
            "label": p.label,
            "description": p.description,
            "rag_enabled": p.rag_enabled,
            "max_tokens": p.max_tokens,
        }
        for p in profiles
    ]


class CreateConversationRequest(BaseModel):
    model_profile_id: str


class CreateConversationResponse(BaseModel):
    conversation_id: str
    model_profile_id: str

# response_model=CreateConversationResponse
@api_router.post("/conversations")
def create_conversation(req: CreateConversationRequest):
    """
    Explicit conversation creation with model profile binding.
    """
    if not req.model_profile_id:
        raise HTTPException(
            status_code=400,
            detail="model_profile_id is required"
        )

    try:
        profile = get_profile(req.model_profile_id)
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model profile: {req.model_profile_id}"
        )

    conversation_id = str(uuid4())

    store = SQLiteMemoryStore()
    store.ensure_conversation(conversation_id, profile.id)

    return {
        "conversation_id": conversation_id,
        "model_profile_id": profile.id,
    }


# --------------------------------------------------
# SYSTEM ROUTES (infra)
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    verify_models()
    return {
        "status": "ready",
        "rag_enabled": ENABLE_RAG,
    }


@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()


# --------------------------------------------------
# CHAT ROUTE
# --------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, _: None = Depends(require_api_key)):
    return router.route(request)


# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large"},
        )
    return await call_next(request)


# --------------------------------------------------
# ROUTER REGISTRATION (FINAL STEP)
# --------------------------------------------------

app.include_router(api_router)
