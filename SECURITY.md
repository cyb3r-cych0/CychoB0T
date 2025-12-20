# Security Policy

## Supported Versions
Only the latest main branch is supported.

## Security Principles
- Runtime-only secrets
- No hardcoded or auto-generated keys
- No secret persistence (disk, memory, vector stores)
- Strict memory isolation per conversation
- Offline-first by default

## Secret Management
Secrets must be provided via environment variables:

```env
API_KEYS=key1,key2
```

- Multiple keys supported
- Rotation supported
- No .env committed (gitignored)

## Reporting Vulnerabilities

**Please do not open public issues for security concerns.**

Email: minigates21@gmail.com

**Include:**

- Description
- Reproduction steps
- Impact assessment

**Out of Scope**

- Model hallucinations
- Prompt misuse
- Third-party LLM outages