import time
import threading

class CircuitBreaker:
    def __init__(self, threshold=3, reset_timeout=60):
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure = 0
        self.state = "CLOSED"
        self.lock = threading.Lock()

    def allow(self):
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure > self.reset_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            return True

    def success(self):
        with self.lock:
            self.failures = 0
            self.state = "CLOSED"

    def failure(self):
        with self.lock:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = "OPEN"
