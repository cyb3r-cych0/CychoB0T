import json
from datetime import datetime


def log_audit_event(
    conversation_id: str,
    engine: str,
    latency_ms: int,
    status: str
):
    event = {
        "timestamp": datetime.now().isoformat(),
        "event": "audit",
        "conversation_id": conversation_id,
        "engine": engine,
        "latency_ms": latency_ms,
        "status": status
    }

    # stdout JSON log
    print(json.dumps(event))
