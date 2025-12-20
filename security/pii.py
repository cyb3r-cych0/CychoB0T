"""
Privacy & Data Handling (Industry-Grade)
Goal:
make privacy enforceable by design, not by convention.
Add:
- PII redaction hooks
- Privacy modes (strict vs relaxed) that actually change behavior
- Data retention controls
- Log hygiene (no sensitive data in logs)
- All offline-safe, configurable, and testable.

Privacy Policy/ Modes

strict:
- Redact PII before storage
- Do not persist assistant responses containing PII
- Minimal logging (no content)
relaxed:
- Store content normally
- Still redact obvious secrets (API keys, passwords)
- PII scope (v1)
- Email addresses
- Phone numbers
- Credit card–like numbers
- API keys / tokens
(Heuristics now, ML later.)
"""

import re

_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{10,15}\b"), "[REDACTED_NUMBER]"),
    (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), "[REDACTED_CARD]"),
    (re.compile(r"(sk-|api-|key-)[A-Za-z0-9]{10,}"), "[REDACTED_SECRET]"),
]

def redact_pii(text: str) -> str:
    redacted = text
    for pattern, repl in _PATTERNS:
        redacted = pattern.sub(repl, redacted)
    return redacted
