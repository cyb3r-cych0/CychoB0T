from dataclasses import dataclass
from pydantic import BaseModel
from typing import Dict, Optional


@dataclass
class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    model_profile_id: str = "general"
    user_mode: str = "auto"
    privacy_mode: str = "strict"
    metadata: Optional[Dict] = None

    @property
    def prompt_length(self) -> int:
        return len(self.message)


@dataclass
class ChatResponse:
    text: str
    engine: str              # offline | online
    model: str
    latency_ms: int
    tokens_used: Optional[int]
