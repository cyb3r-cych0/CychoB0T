![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Status](https://img.shields.io/badge/status-stable-green)
![Security](https://img.shields.io/badge/security-runtime--only-critical)
![Offline](https://img.shields.io/badge/offline--first-yes-success)


# Hybrid Offline-First Chatbot Backend

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

## Quick Start

```bash
export API_KEYS=sk-xxxx
uvicorn api:app --reload
```

## Contributing

See `CONTRIBUTING.md`

## License

MIT License. See the [LICENSE](LICENSE) file.

## Author

Built as an industry-grade backend, not a demo — with a focus on correctness, safety, and long-term maintainability.
