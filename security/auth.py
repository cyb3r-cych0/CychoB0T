from fastapi import Header, HTTPException
from security.api_keys import load_api_keys
from security.rate_limit import rate_limit
import logging

logger = logging.getLogger("security")


def require_api_key(x_api_key: str = Header(...)):
    keys = load_api_keys()

    if x_api_key not in keys:
        logger.warning("auth_failed")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # rate limit AFTER auth
    try:
        rate_limit(x_api_key)
    except HTTPException:
        logger.warning("rate_limit_exceeded", extra={"api_key": x_api_key})
        raise

