import time
import requests
from core.interfaces import LLMEngine
from core.schemas import ChatRequest, ChatResponse
from infra.settings import OFFLINE_URL, OFFLINE_TIMEOUT


class OfflineLLMServer(LLMEngine):
    def generate(self, request: ChatRequest) -> ChatResponse:
        start = time.time()

        payload = {
            "prompt": f"<s>[INST] {request.message} [/INST]",
            "n_predict": 512,
            "temperature": 0.7
        }

        r = requests.post(
            OFFLINE_URL,
            json=payload,
            timeout=OFFLINE_TIMEOUT
        )

        r.raise_for_status()

        latency = int((time.time() - start) * 1000)

        return ChatResponse(
            text=r.json()["content"],
            engine="offline",
            model="mistral-server",
            latency_ms=latency,
            tokens_used=None
        )
