from infra.settings import OFFLINE_BACKEND


def get_offline_engine(profile):
    if OFFLINE_BACKEND == "embedded":
        from engines.offline_embedded import OfflineLLMEmbedded
        return OfflineLLMEmbedded(profile)

    if OFFLINE_BACKEND == "server":
        from engines.offline_server import OfflineLLMServer
        return OfflineLLMServer()

    raise ValueError(f"Invalid OFFLINE_BACKEND: {OFFLINE_BACKEND}")
