![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![Status](https://img.shields.io/badge/status-stable-green)
![Security](https://img.shields.io/badge/security-runtime--only-critical)
![Offline](https://img.shields.io/badge/offline--first-yes-success)


# CychoB0T — Hybrid Offline-First Chatbot

A production-grade, **offline-first chatbot backend** with secure runtime-only secrets,
memory isolation, and optional online LLM fallback.

Designed for **privacy-sensitive, research, and enterprise deployments**.

## Features
- Offline-first LLM routing (llama.cpp)
- Optional online fallback with circuit breaker
- Per-conversation isolated memory
- Vector-based long-term memory with decay
- Secure env-only API keys (rotation-ready)
- RAG with privacy modes
- Docker & CI ready

## Security
- No secrets on disk
- No secrets in memory or vector DBs
- Environment variables only
- Multiple API keys + rotation supported

## ▶ How to Run

### PART 1 — Embedded mode (NO llama server | No UI)

Goal
- Prove the Python-embedded LLM works
- No extra terminals
- Concurrency enforced = 1

**Step 1 — Set environment**

- Windows (PowerShell)
```powershell
$env:OFFLINE_BACKEND="embedded"
```

- Linux / macOS
```bash
export OFFLINE_BACKEND=embedded
```

**Step 2 — Ensure dependency exists**
```bash
pip install llama-cpp-python
```

**Step 3 — Start backend ONLY**
```bash
uvicorn api.server:app --port 8000
```

You should see:
- FastAPI startup logs
- NO llama-server logs
- No port 8080 usage

**Step 4 — Verify embedded mode**

***4.1 Check metrics***

- Open:
```arduino
http://127.0.0.1:8000/metrics
```

- You should see:

```json
"gauges": {
  "offline_backend_mode": 1,
  "offline_concurrency_limit": 1,
  "offline_inflight": 0
}
```

***4.2 Send a test request***

- Via Swagger:
```arduino
http://127.0.0.1:8000/docs
```

- Payload:
```json
{
  "message": "Hello from embedded mode",
  "conversation_id": "test-embedded",
  "user_mode": "offline_only",
  "privacy_mode": "standard",
  "metadata": {}
}
```

Expected:
- Response completes
- engine = "offline"
- No 503
- Takes a few seconds (normal)

***4.3 Concurrency test (IMPORTANT)****

- Send two requests quickly.
- Expected:
    - First → succeeds
    - Second → 503 Offline model is busy

- Metrics update:
```json
"offline_model_busy": 1
```

### PART 2 — Server mode (llama.cpp HTTP | No UI)

Goal
- Backend talks to external llama server
- Concurrency > 1 allowed
- Crash isolation

**Step 5 — Stop backend**
```bash
Ctrl + C
```

**Step 6 — Set server mode**

- Windows
```powershell
$env:OFFLINE_BACKEND="server"
```


- Linux / macOS
```bash
export OFFLINE_BACKEND=server
```


**Step 7 — Start llama.cpp server (NEW TERMINAL)**
```bash
./llama-server -m models/mistral-7b-instruct-v0.1.Q4_K_M.gguf --port 8080
```

- Wait until you see:
```ngix
server listening on 0.0.0.0:8080
```

**Step 8 — Start backend (again)**
```bash
uvicorn api.server:app --port 8000
```

**Step 9 — Verify server mode**

***9.1 Check metrics***
```arduino
http://127.0.0.1:8000/metrics
```

- Expected:
```json
"gauges": {
  "offline_backend_mode": 2,
  "offline_concurrency_limit": <MAX_CONCURRENT_REQUESTS>,
  "offline_inflight": 0
}
```

***9.2 Send test request***

- Payload:
```json
{
  "message": "Hello from server mode",
  "conversation_id": "test-server",
  "user_mode": "offline_only",
  "privacy_mode": "standard",
  "metadata": {}
}
```

- Expected:
  - Response returns normally
  - Faster than embedded
  - Multiple concurrent requests work

***9.3 Kill llama server (failure test)***

- Stop llama server terminal.
- Send another request.
- Expected:
    - Backend returns 503
    - Clean log:
```json
"online_engine_failed_fallback"
```

### Run via Streamlit — User Interface

**A. Streamlit + Embedded backend (NO llama server | Yes UI)**

1. Set environment

- Windows (PowerShell)
```powershell
$env:OFFLINE_BACKEND="embedded"
```

- Linux / macOS
```bash
export OFFLINE_BACKEND=embedded
```

2. Start backend (Terminal 1)
```bash
uvicorn api.server:app --port 8000
```

- ✔ This loads llama-cpp-python
- ✔ No port 8080 should be in use

3. Start Streamlit (Terminal 2)
```bash
streamlit run frontend/app.py
```

- This opens:
```arduino
http://localhost:8501
```

4. Verify in Streamlit UI

- In the app:
  - Send: “Hello from Streamlit embedded”
  - Expect:
      - Response appears normally
      - Slightly slower first response (model load)
      - Metrics panel shows:
        - Backend: Embedded
        - Concurrency: 0/1 → 1/1
  - Double-send quickly:
      - Second request shows:
         - “Offline model is currently busy. Please wait…”

**B. Streamlit + Server backend (llama.cpp HTTP | Yes UI)**

5. Stop Everything
```bash
Ctrl + C
```
- (stop both backend + streamlit)

6. Set Server Mode

- Windows
```powershell
$env:OFFLINE_BACKEND="server"
```

- Linux / macOS
```bash
export OFFLINE_BACKEND=server
```

7. Start llama.cpp server (Terminal 1)
```bash
./llama-server -m models/mistral-7b-instruct-v0.1.Q4_K_M.gguf --port 8080
```

- wait until you see
```ngix
listening on 0.0.0.0:8080
```

8. Start Backend (terminal 2)
```bash
uvicorn api.server:app --port 8000
```

9. Start Streamlit (Terminal 3)
```bash
streamlit run frontend/app.py
```

10. Verify in Streamlit UI

- Send: “Hello from Streamlit server mode”
- Expect:
- Faster response
  - Multiple quick sends work
  - Metrics show:
    - Backend: Server
    - Concurrency: 0/N

- Stop llama server and send again:
  - UI shows friendly:
    - “Offline model unavailable / busy”
  - Backend does not crash

### Run everything with Docker
```bash
docker compose up --build
```

### Mental Model

```bash
Streamlit UI
   ↓
FastAPI (/chat)
   ↓
Router
   ↓
Offline engine
   ├─ embedded → llama-cpp-python
   └─ server   → llama.cpp HTTP
```
**Verify:**

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Make sure:**

- Backend is running
- API key is set in .streamlit/secrets.toml

### Environment variables

```bash
ENABLE_RAG=true
OFFLINE_URL=http://localhost:8080/completion
ONLINE_URL=http://127.0.0.1:9999/completion  # optional
```

## Contributing

See `CONTRIBUTING.md`

## License

MIT License. See the [LICENSE](LICENSE) file.

## Author

`cyb3r-cych0`