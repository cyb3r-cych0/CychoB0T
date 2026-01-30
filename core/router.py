import time
from fastapi import HTTPException

from memory.sqlite_store import SQLiteMemoryStore
from memory.short_term import ShortTermMemory
from infra.connectivity import ConnectivityService
from infra.circuit_breaker import CircuitBreaker
from infra.concurrency import ConcurrencyLimiter
from infra.runtime import shutdown_event
from infra.metrics import metrics
from infra.audit import log_audit_event
from infra.sanitize import sanitize_prompt
from engines.online_llm import OnlineLLM
from engines.offline_factory import get_offline_engine
from models.registry import get_profile

from infra.settings import (
        MAX_CONCURRENT_REQUESTS,
        MAX_CONTEXT_CHARS,
        MAX_PROMPT_CHARS,
        ENABLE_RAG,
        RAG_TOP_K,
        RAG_MAX_CHARS
    )
from infra.observability import (
    log_request_received,
    log_engine_selected,
    log_response_generated,
    log_online_fallback,
    log_input_rejected,
    log_latency
)
from security.pii import redact_pii


class Router:
    def __init__(self):
        self.offline = get_offline_engine
        self.online = OnlineLLM()
        self.store = SQLiteMemoryStore()
        self.short = ShortTermMemory()
        self.circuit = CircuitBreaker()
        self.limiter = ConcurrencyLimiter(
            max_concurrent=MAX_CONCURRENT_REQUESTS
        )
        self.enable_rag = ENABLE_RAG

        if self.enable_rag:
            from rag.embeddings import EmbeddingModel
            from rag.vector_store import SQLiteVectorStore
            from rag.retriever import Retriever
            from rag.augment import augment_prompt

            self.embedder = EmbeddingModel()
            self.vstore = SQLiteVectorStore()
            self.retriever = Retriever(self.vstore)
            self._augment_prompt = augment_prompt

    def route(self, request):
        #validate profile ID
        try:
            get_profile(request.model_profile_id)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model profile: {request.model_profile_id}"
            )

        # metrics + shutdown
        metrics.inc("requests_total")

        if shutdown_event.is_set():
            metrics.inc("errors_total")
            log_audit_event(
                conversation_id=request.conversation_id,
                engine="system",
                latency_ms=0,
                status="shutdown",
            )
            raise HTTPException(
                status_code=503,
                detail="Server shutting down"
            )

        start = time.time()

        log_request_received(
            request.conversation_id,
            request.user_mode
        )

        # validation
        if not request.message or not isinstance(request.message, str):
            log_input_rejected("empty_or_non_text")
            metrics.inc("errors_total")
            log_audit_event(
                conversation_id=request.conversation_id,
                engine="none",
                latency_ms=0,
                status="rejected",
            )
            raise HTTPException(
                status_code=422,
                detail="Message must be non-empty text"
            )

        if request.prompt_length > MAX_PROMPT_CHARS:
            log_input_rejected("prompt_too_long")
            metrics.inc("errors_total")
            log_audit_event(
                conversation_id=request.conversation_id,
                engine="none",
                latency_ms=0,
                status="rejected",
            )
            raise HTTPException(
                status_code=413,
                detail=f"Prompt exceeds {MAX_PROMPT_CHARS} characters"
            )

        # Fail if conversation does not exist
        if not self.store.conversation_exists(request.conversation_id):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Conversation does not exist. "
                    "Create it first via POST /conversations."
                )
            )

        # conversation setup + validation
        # self.store.ensure_conversation(
        #     request.conversation_id,
        #     request.model_profile_id
        # )
        stored_profile_id = self.store.get_model_profile_id(request.conversation_id)
        profile = get_profile(stored_profile_id)

        if stored_profile_id != request.model_profile_id:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Model profile is locked for this conversation. "
                    "Start a new conversation to change models."
                )
            )

        if self.short.conversation_id != request.conversation_id:
            self.short.reset(request.conversation_id)

        raw_user_message = request.message

        # prompt build
        request.message = self.short.build_prompt(request.message)

        # privacy + store user message
        content_to_store = request.message
        if request.privacy_mode == "strict":
            content_to_store = redact_pii(content_to_store)

        self.store.add_message(
            conversation_id=request.conversation_id,
            role="user",
            content=content_to_store,
            engine="user",
        )

        # Optional RAG augmentation
        if self.enable_rag:
            q_emb = self.embedder.embed([request.message])[0]
            chunks = self.retriever.search(
                query_emb=q_emb,
                k=RAG_TOP_K,
                privacy_mode=request.privacy_mode,
                owner=request.conversation_id
            )
            request.message = self._augment_prompt(
                request.message,
                chunks,
                max_retrieved_chars=RAG_MAX_CHARS
            )

        # Context Explosion Guard
        if len(request.message) > MAX_CONTEXT_CHARS:
            request.message = request.message[-MAX_CONTEXT_CHARS:]

        # routing + fallback
        try:
            with self.limiter:
                offline_engine = self.offline(profile)
                if (
                    request.user_mode == "offline_only"
                    or not ConnectivityService.is_online()
                ):
                    try:
                        response = offline_engine.generate(request, profile)
                        metrics.inc("engine_offline")
                    except Exception:
                        metrics.inc("errors_total")
                        log_audit_event(
                            conversation_id=request.conversation_id,
                            engine="offline",
                            latency_ms=0,
                            status="failed",
                        )
                        raise HTTPException(
                            status_code=503,
                            detail="Offline model unavailable"
                        )
                else:
                    if not self.circuit.allow():
                        try:
                            response = offline_engine.generate(request, profile)
                            metrics.inc("engine_offline")
                        except Exception:
                            metrics.inc("errors_total")
                            log_audit_event(
                                conversation_id=request.conversation_id,
                                engine="offline",
                                latency_ms=0,
                                status="failed",
                            )
                            raise HTTPException(
                                status_code=503,
                                detail="Offline model unavailable"
                            )
                    else:
                        try:
                            response = self.online.generate(request)
                            self.circuit.success()
                            metrics.inc("engine_online")
                        except Exception:
                            self.circuit.failure()
                            log_online_fallback("online_engine_unreachable")
                            try:
                                response = offline_engine.generate(request, profile)
                                metrics.inc("engine_offline")
                            except Exception:
                                metrics.inc("errors_total")
                                log_audit_event(
                                    conversation_id=request.conversation_id,
                                    engine="offline",
                                    latency_ms=0,
                                    status="failed",
                                )
                                raise HTTPException(
                                    status_code=503,
                                    detail="Offline model unavailable"
                                )
        except RuntimeError as e:
            if str(e) == "model_busy":
                metrics.inc("errors_total")
                metrics.inc("offline_model_busy")
                raise HTTPException(
                    status_code=503,
                    detail="Offline model is busy. Please wait and try again."
                )
            raise

        # post response
        latency = int((time.time() - start) * 1000)
        metrics.observe("latency_ms", latency)

        log_engine_selected(response.engine)
        log_latency(response.engine, latency)
        log_response_generated(
            request.conversation_id,
            response.engine,
            latency,
        )

        assistant_content = sanitize_prompt(response.text)
        if request.privacy_mode == "strict":
            assistant_content = redact_pii(assistant_content)

        self.store.add_message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=assistant_content,
            engine=response.engine,
        )

        # update short-term buffer: use RAW user message, not augmented prompt
        self.short.add("user", raw_user_message)
        self.short.add("assistant", response.text)

        log_audit_event(
            conversation_id=request.conversation_id,
            engine=response.engine,
            latency_ms=latency,
            status="success",
        )

        return response
