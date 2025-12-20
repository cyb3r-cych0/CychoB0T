# Internal Security Guarantees

## Secret Handling
- Environment variables only
- No disk writes
- No defaults
- No logs

## Threat Model
- Accidental secret leakage
- Cross-session data bleed
- Silent fallback failures

## Mitigations
- Explicit configuration
- Fail-fast startup checks
- Audit logging
