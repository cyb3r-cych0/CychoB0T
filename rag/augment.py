"""
Augment the user prompt with retrieved context
Hard bounds on added context
Never exceed MAX_CONTEXT_CHARS
"""
from infra.settings import MAX_CONTEXT_CHARS


def augment_prompt(prompt: str, chunks: list[str], max_retrieved_chars: int) -> str:
    # 1. Trim retrieved context first (soft cap)
    context_parts = []
    total = 0

    for c in chunks:
        if total + len(c) > max_retrieved_chars:
            break
        context_parts.append(c)
        total += len(c)

    context = "\n---\n".join(context_parts)

    augmented = f"Context:\n{context}\n\nQuestion:\n{prompt}"

    # 2. HARD CAP final prompt (non-negotiable)
    if len(augmented) > MAX_CONTEXT_CHARS:
        augmented = augmented[-MAX_CONTEXT_CHARS:]

    return augmented

