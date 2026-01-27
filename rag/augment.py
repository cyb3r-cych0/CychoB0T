"""
Augment the user prompt with retrieved context
Hard bounds on added context
Never exceed MAX_CONTEXT_CHARS
"""
from infra.sanitize import sanitize_prompt
from infra.settings import MAX_CONTEXT_CHARS

def augment_prompt(prompt: str, chunks: list[str], max_retrieved_chars: int) -> str:
    context_parts = []
    total = 0

    for c in chunks:
        clean = sanitize_prompt(c)
        if total + len(clean) > max_retrieved_chars:
            break
        context_parts.append(clean)
        total += len(clean)

    context = "\n---\n".join(context_parts)

    augmented = (
        f"Context:\n{context}\n\n"
        f"Question:\n{sanitize_prompt(prompt)}"
    )

    # hard cap
    if len(augmented) > MAX_CONTEXT_CHARS:
        augmented = augmented[-MAX_CONTEXT_CHARS:]

    return augmented
