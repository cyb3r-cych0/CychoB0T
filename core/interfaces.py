from abc import ABC, abstractmethod
from core.schemas import ChatRequest, ChatResponse


class LLMEngine(ABC):
    @abstractmethod
    def generate(self, request: ChatRequest, profile) -> ChatResponse:
        pass
