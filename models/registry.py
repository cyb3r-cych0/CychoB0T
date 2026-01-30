from typing import Dict, List
from .profiles import ModelProfile

_PROFILES: Dict[str, ModelProfile] = {
    "general": ModelProfile(
        id="general",
        label="General Assistant",
        description="General-purpose assistant",
        engine_type="offline",
        model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        context_window=4096,
        max_tokens=512,
        temperature=0.7,
        rag_enabled=True,
    ),
    "code": ModelProfile(
        id="code",
        label="Code Assistant",
        description="Optimized for programming tasks",
        engine_type="offline",
        model_path="models/mistral-7b-uncensored.Q8_0.gguf",
        context_window=8192,
        max_tokens=768,
        temperature=0.3,
        rag_enabled=False,
    ),
}

def list_profiles() -> List[ModelProfile]:
    return list(_PROFILES.values())

def get_profile(profile_id: str) -> ModelProfile:
    if profile_id not in _PROFILES:
        raise KeyError(f"Unknown model profile: {profile_id}")
    return _PROFILES[profile_id]

