import os
from fastapi import HTTPException
from infra.settings import API_KEYS

def load_api_keys() -> list[str]:
    try:
        raw = os.getenv(API_KEYS)
        if not raw:
            raise RuntimeError()
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if not keys:
            raise RuntimeError()
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail=f"{API_KEYS} not set. Check if your API key is valid."
        )
    return keys
