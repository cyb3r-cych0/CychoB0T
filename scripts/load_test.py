import requests
import threading
import time

URL = "http://127.0.0.1:8000/chat"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "dev-key-123"
}

def worker(i):
    payload = {
        "message": f"load test {i}",
        "conversation_id": f"load-{i%3}",
        "user_mode": "auto",
        "privacy_mode": "standard",
        "metadata": {}
    }
    try:
        r = requests.post(URL, json=payload, headers=HEADERS, timeout=10)
        print(i, r.status_code)
    except Exception as e:
        print(i, "error", e)

threads = []
start = time.time()

for i in range(20):
    t = threading.Thread(target=worker, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Completed in", int((time.time() - start) * 1000), "ms")
