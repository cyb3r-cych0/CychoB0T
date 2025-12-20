# Architecture Deep Dive

## Design Principles
- Offline-first by default
- Explicit failure handling
- No implicit state
- Strong memory isolation
- Runtime-only secrets

## Request Lifecycle
1. Client sends request
2. API gateway validates input
3. LLM router selects execution path
4. Memory manager scopes context
5. RAG pipeline augments prompt (if enabled)
6. Response generated
7. Metrics + audit logs emitted

## LLM Routing
- Primary: local inference (llama.cpp)
- Secondary: online provider
- Circuit breaker prevents cascading failures
- Key rotation on quota / rate limits

## Failure Modes
| Component             | Behavior               |
|-----------------------|------------------------|
| Local LLM unavailable | Fallback to online     |
| Online quota hit      | Rotate key / fail fast |
| Memory corruption     | Drop context, continue |


```text
┌──────────┐
│  Client  │
└────┬─────┘
     ▼
┌────────────────────┐
│ FastAPI Gateway    │
└────┬───────────────┘
     ▼
┌──────────────────────────────┐
│ LLM Router                   │
│  ├─ Offline (llama.cpp)      │
│  └─ Online Fallback          │
│      └─ Circuit Breaker      │
└────┬─────────────────────────┘
     ▼
┌──────────────────────────────┐
│ Memory Manager                │
│  ├─ Short-term (per session) │
│  └─ Long-term (vector+decay) │
└────┬─────────────────────────┘
     ▼
┌──────────────────────────────┐
│ RAG Pipeline                  │
│  ├─ Privacy Modes             │
│  └─ Context Filters           │
└────┬─────────────────────────┘
     ▼
┌──────────────────────────────┐
│ Metrics & Audit Logging       │
└──────────┬───────────────────┘
           ▼
        Response
```