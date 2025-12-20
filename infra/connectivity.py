import time
import requests


class ConnectivityService:
    _last_check = 0
    _is_online = False
    _ttl = 10  # seconds

    @classmethod
    def is_online(cls) -> bool:
        now = time.time()

        if now - cls._last_check < cls._ttl:
            return cls._is_online

        try:
            requests.get("https://1.1.1.1", timeout=2)
            cls._is_online = True
        except requests.RequestException:
            cls._is_online = False

        cls._last_check = now
        return cls._is_online
