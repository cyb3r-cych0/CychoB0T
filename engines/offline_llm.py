from llama_cpp import Llama
from core.schemas import ChatResponse
from infra.settings import LLAMA_VERBOSE


class OfflineLLM:
    def __init__(self, model_path: str, n_ctx: int):
        self.model_path = model_path
        self.n_ctx = n_ctx

        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=8,
            n_batch=512,
            verbose=LLAMA_VERBOSE,
        )

    def generate(self, request, *, max_tokens: int, temperature: float):
        output = self.llm(
            prompt=request.message,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>"],
        )

        return ChatResponse(
            text=output["choices"][0]["text"].strip(),
            engine="offline",
            model=self.model_path.split("/")[-1],
            latency_ms=0,
            tokens_used=None,
        )
