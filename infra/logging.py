"""
Logs include IDs, engine, latency
❌ No message, content, or prompt text
"""
import logging
import sys
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # capture extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno",
                "pathname", "filename", "module", "exc_info",
                "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process"
            ):
                log[key] = value

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log)


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
