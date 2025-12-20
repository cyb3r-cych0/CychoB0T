# Memory Model

## Short-Term Memory
- Scoped per conversation
- Ephemeral
- Strict token limits
- Never persisted

## Long-Term Memory
- Vector-based
- Decay enforced
- Explicit opt-in
- No secrets stored

## Global Memory
- Intentionally disabled
- Prevents cross-user leakage

## Invariants
- No implicit memory sharing
- No background accumulation
- No secret persistence
