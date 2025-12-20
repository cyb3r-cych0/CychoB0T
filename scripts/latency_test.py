import time
import requests

URL = "http://127.0.0.1:8000/chat"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "dev-key-123"
}

payload = {
    "message": "Explain ransomware in one sentence",
    "conversation_id": "latency-test",
    "user_mode": "auto",
    "privacy_mode": "strict",
    "metadata": {}
}

times = []

for i in range(10):
    start = time.time()
    r = requests.post(URL, json=payload, headers=HEADERS)
    elapsed = int((time.time() - start) * 1000)
    times.append(elapsed)
    print(f"Run {i+1}: {elapsed} ms")

print("\nSummary")
print(f"min={min(times)} ms")
print(f"p50={sorted(times)[len(times)//2]} ms")
print(f"p95={sorted(times)[int(len(times)*0.95)]} ms")
print(f"max={max(times)} ms")
