from dataclasses import dataclass
from typing import Literal, Optional

EngineType = Literal["offline", "online", "embedded"]

@dataclass(frozen=True)
class ModelProfile:
    id: str
    label: str
    description: str
    engine_type: EngineType
    model_path: Optional[str]          # local path or remote endpoint key
    context_window: int
    max_tokens: int
    temperature: float
    rag_enabled: bool
