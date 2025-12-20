import time
import requests
from core.interfaces import LLMEngine
from core.schemas import ChatRequest, ChatResponse
from infra.settings import ONLINE_URL, RETRIES, RETRY_BASE_DELAY, ONLINE_TIMEOUT
from infra.retry import retry_request


class OnlineLLM(LLMEngine):
    def generate(self, request: ChatRequest) -> ChatResponse:
        start = time.time()

        payload = {
            "prompt": f"<s>[INST] {request.message} [/INST]",
            "n_predict": 512,
            "temperature": 0.7
        }

        def call():
            return requests.post(
                ONLINE_URL,
                json=payload,
                timeout=ONLINE_TIMEOUT
            )

        # retries + backoff
        r = retry_request(
            call,
            retries=RETRIES,
            base_delay=RETRY_BASE_DELAY
        )

        latency = int((time.time() - start) * 1000)

        #  response format
        data = r.json()

        if "content" in data:
            text = data["content"]
        elif "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0].get("text", "")
        else:
            text = r.text

        return ChatResponse(
            text=text,
            engine="online",
            model="mistral-remote",
            latency_ms=latency,
            tokens_used=None
        )
