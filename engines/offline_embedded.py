import time
from llama_cpp import Llama
from core.interfaces import LLMEngine
from core.schemas import ChatRequest, ChatResponse
from infra.settings import MAX_CONTEXT_CHARS


class OfflineLLMEmbedded(LLMEngine):
    def __init__(self):
        self.llm = Llama(
            model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            n_ctx=4096,
            n_threads=6,
            verbose=False
        )

    def generate(self, request: ChatRequest) -> ChatResponse:
        start = time.time()

        prompt = f"<s>[INST] {request.message} [/INST]"

        result = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            stop=["</s>"]
        )

        latency = int((time.time() - start) * 1000)

        return ChatResponse(
            text=result["choices"][0]["text"].strip(),
            engine="offline",
            model="mistral-embedded",
            latency_ms=latency,
            tokens_used=None
        )
