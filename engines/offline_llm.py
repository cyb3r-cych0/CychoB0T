import time
import requests
from core.interfaces import LLMEngine
from core.schemas import ChatRequest, ChatResponse
from infra.settings import OFFLINE_URL, OFFLINE_TIMEOUT


class OfflineLLM(LLMEngine):

    def generate(self, request: ChatRequest) -> ChatResponse:
        start = time.time()

        payload = {
            "prompt": f"<s>[INST] {request.message} [/INST]",
            "n_predict": 256,
            "temperature": 0.7,
            "top_p": 0.9
        }

        r = requests.post(
            OFFLINE_URL,
            json=payload,
            timeout=OFFLINE_TIMEOUT
        )

        latency = int((time.time() - start) * 1000)

        #  response format
        data = r.json()

        if "content" in data:
            text = data["content"]
        elif "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0].get("text", "")
        else:
            text = r.text  # last-resort fallback

        return ChatResponse(
            text=text,
            engine="offline",
            model="mistral-7b-instruct",
            latency_ms=latency,
            tokens_used=None
        )
