import time
from fastapi import HTTPException

from infra.connectivity import ConnectivityService
from engines.offline_llm import OfflineLLM
from engines.online_llm import OnlineLLM
from memory.sqlite_store import SQLiteMemoryStore
from memory.short_term import ShortTermMemory
from security.pii import redact_pii
from infra.circuit_breaker import CircuitBreaker
from infra.concurrency import ConcurrencyLimiter
from infra.runtime import shutdown_event
from infra.metrics import metrics
from infra.audit import log_audit_event


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
    log_latency,
)


class Router:
    def __init__(self):
        self.offline = OfflineLLM()
        self.online = OnlineLLM()
        self.store = SQLiteMemoryStore()
        self.short = ShortTermMemory()
        self.circuit = CircuitBreaker()
        self.limiter = ConcurrencyLimiter(max_concurrent=MAX_CONCURRENT_REQUESTS)
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
        metrics.inc("requests_total")

        if shutdown_event.is_set():
            metrics.inc("errors_total")
            log_audit_event(
                conversation_id=request.conversation_id,
                engine="system",
                latency_ms=0,
                status="shutdown"
            )
            raise HTTPException(status_code=503, detail="Server shutting down")

        # logging
        start = time.time()

        log_request_received(
            request.conversation_id,
            request.user_mode
        )

        # Reset short-term memory on new conversation
        if self.short.conversation_id != request.conversation_id:
            self.short.reset(request.conversation_id)

        # raw user message check
        if not isinstance(request.message, str):
            log_input_rejected("non_text_message")
            metrics.inc("errors_total")
            log_audit_event(
                conversation_id=request.conversation_id,
                engine="none",
                latency_ms=0,
                status="rejected"
            )
            raise HTTPException(status_code=422, detail="Message must be text")

        if request.prompt_length > MAX_PROMPT_CHARS:
            log_input_rejected("prompt_too_long")
            metrics.inc("errors_total")
            log_audit_event(
                conversation_id=request.conversation_id,
                engine="none",
                latency_ms=0,
                status="rejected"
            )
            raise HTTPException(status_code=413, detail=f"Prompt exceeds {MAX_PROMPT_CHARS} characters")

        self.store.ensure_conversation(request.conversation_id)

        # build context-enhanced prompt
        request.message = self.short.build_prompt(request.message)

        # Redact PII before storage
        content_to_store = request.message
        if request.privacy_mode == "strict":
            content_to_store = redact_pii(content_to_store)

        # persist user message
        self.store.add_message(
            conversation_id=request.conversation_id,
            role="user",
            content=content_to_store,
            engine="user"
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
        with self.limiter:
            if request.user_mode == "offline_only" or not ConnectivityService.is_online():
                try:
                    response = self.offline.generate(request)
                    metrics.inc("engine_offline")
                except Exception:
                    metrics.inc("errors_total")
                    log_audit_event(
                        conversation_id=request.conversation_id,
                        engine="none",
                        latency_ms=0,
                        status="rejected"
                    )
                    raise HTTPException(
                        status_code=503,
                        detail="Offline model unavailable"
                    )
            else:
                if not self.circuit.allow():
                    try:
                        response = self.offline.generate(request)
                        metrics.inc("engine_offline")
                    except Exception:
                        metrics.inc("errors_total")
                        log_audit_event(
                            conversation_id=request.conversation_id,
                            engine="none",
                            latency_ms=0,
                            status="rejected"
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
                        try:
                            response = self.offline.generate(request)
                            metrics.inc("engine_offline")
                        except Exception:
                            metrics.inc("errors_total")
                            log_audit_event(
                                conversation_id=request.conversation_id,
                                engine="none",
                                latency_ms=0,
                                status="rejected"
                            )
                            raise HTTPException(
                                status_code=503,
                                detail="Offline model unavailable"
                            )
        # logging
        try:
            log_engine_selected("offline")

        except Exception as e:
            log_online_fallback(e)
            response = self.offline.generate(request)

        latency = int((time.time() - start) * 1000)
        metrics.observe("latency_ms", latency)

        log_latency(
            response.engine,
            latency
        )

        log_response_generated(
            request.conversation_id,
            response.engine,
            latency
        )

        # The user still receives the original response. Only storage is sanitized.
        assistant_content = response.text

        if request.privacy_mode == "strict":
            assistant_content = redact_pii(assistant_content)

        # persist assistant message
        self.store.add_message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=assistant_content,
            engine=response.engine
        )

        # update short-term buffer
        self.short.add("user", request.message)
        self.short.add("assistant", response.text)

        log_audit_event(
            conversation_id=request.conversation_id,
            engine=response.engine,
            latency_ms=latency,
            status="success"
        )

        return response
