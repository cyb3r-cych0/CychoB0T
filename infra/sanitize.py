ROLE_TOKENS = [
    "[USER]",
    "[ASSISTANT]",
    "[INST]",
    "[/INST]",
    "<s>",
    "</s>",
]


def sanitize_prompt(text: str) -> str:
    if not text:
        return text

    for token in ROLE_TOKENS:
        text = text.replace(token, "")

    return text.strip()
