# from dataclasses import dataclass
# from typing import Dict
#
#
# @dataclass(frozen=True)
# class ModelProfile:
#     id: str
#     label: str
#     model_path: str
#     temperature: float
#     max_tokens: int
#     rag_enabled: bool
#     description: str
#
#
# MODEL_PROFILES: Dict[str, ModelProfile] = {
#     "general": ModelProfile(
#         id="general",
#         label="General Assistant",
#         model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
#         temperature=0.7,
#         max_tokens=512,
#         rag_enabled=False,
#         description="Balanced, general-purpose assistant."
#     ),
#     "code": ModelProfile(
#         id="code",
#         label="Code Assistant",
#         model_path="models/mistral-7b-uncensored.Q8_0.gguf",
#         temperature=0.2,
#         max_tokens=512,
#         rag_enabled=False,
#         description="Low-temperature model for coding and refactors."
#     ),
#     # Add more profiles later (security, long-context, etc.)
# }

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
