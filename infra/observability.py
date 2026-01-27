import logging

logger = logging.getLogger("router")


def log_request_received(conversation_id, user_mode):
    logger.info(
        "request_received",
        extra={
            "conversation_id": conversation_id,
            "user_mode": user_mode
        }
    )


def log_engine_selected(engine):
    logger.info(
        "engine_selected",
        extra={
            "engine": engine
        }
    )


def log_response_generated(conversation_id, engine, latency_ms):
    logger.info(
        "response_generated",
        extra={
            "conversation_id": conversation_id,
            "engine": engine,
            "latency_ms": latency_ms
        }
    )


def log_online_fallback(reason: str):
    logger.warning(
        "online_engine_failed_fallback",
        extra={
            "reason": reason
        }
    )


def log_input_rejected(reason):
    logger.warning(
        "input_rejected",
        extra={"reason": reason
       }
    )


def log_latency(engine, latency_ms):
    logger.info(
        "latency",
        extra={
        "engine": engine,
        "latency_ms": latency_ms
        }
    )


def log_rate_limited(reason):
    logger.warning(
        "rate_limited",
        extra={
            "reason": reason
        }
    )

