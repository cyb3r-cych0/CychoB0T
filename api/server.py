from fastapi import FastAPI
from core.router import Router
from core.schemas import ChatRequest, ChatResponse
from infra.logging import setup_logging
from fastapi import Depends
from security.auth import require_api_key # Protect the API Endpoint
from fastapi import Request
from fastapi.responses import JSONResponse
from infra.settings import MAX_BODY_BYTES, TITLE, VERSION
from infra.preflight import verify_models
from infra.settings import ENABLE_RAG
from contextlib import asynccontextmanager
from infra.runtime import shutdown_event
from infra.metrics import metrics
import time
from dotenv import load_dotenv


load_dotenv()
setup_logging()
router = Router()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    shutdown_event.set()
    time.sleep(0.5)

app = FastAPI(
    title=TITLE,
    version=VERSION,
    lifespan=lifespan
)

from infra.settings import OFFLINE_BACKEND, MAX_CONCURRENT_REQUESTS
from infra.metrics import metrics

limit = 1 if OFFLINE_BACKEND == "embedded" else MAX_CONCURRENT_REQUESTS

metrics.set("offline_concurrency_limit", limit)
metrics.set(
    "offline_backend_mode",
    1 if OFFLINE_BACKEND == "embedded" else 2
)



@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    # fail fast if required assets are missing
    verify_models()

    return {
        "status": "ready",
        "rag_enabled": ENABLE_RAG
    }


@app.get("/models")
def models():
    return {
        "offline": ["mistral-7b-instruct"],
        "online": ["remote-llama-server"]
    }



@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    _: None = Depends(require_api_key)
):
    return router.route(request)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large"}
        )
    return await call_next(request)


@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()