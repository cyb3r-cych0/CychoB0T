from engines.offline_llm import OfflineLLM
from engines.online_llm import OnlineLLM
from models.registry import get_profile
from infra.concurrency import ConcurrencyLimiter
from infra.settings import MAX_CONCURRENT_REQUESTS

class EngineHandle:
    def __init__(self, engine, limiter):
        self.engine = engine
        self.limiter = limiter


class EngineFactory:
    def __init__(self):
        self._engines = {}

    def get(self, profile_id: str) -> EngineHandle:
        if profile_id in self._engines:
            return self._engines[profile_id]

        profile = get_profile(profile_id)

        if profile.engine_type == "offline":
            engine = OfflineLLM(
                model_path=profile.model_path,
                n_ctx=profile.context_window,
            )
        elif profile.engine_type == "online":
            engine = OnlineLLM()
        else:
            raise RuntimeError(f"Unknown engine type: {profile.engine_type}")

        limiter = ConcurrencyLimiter(MAX_CONCURRENT_REQUESTS)

        handle = EngineHandle(engine, limiter)
        self._engines[profile_id] = handle
        return handle
