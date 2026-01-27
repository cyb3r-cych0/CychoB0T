from infra.sanitize import sanitize_prompt

class ShortTermMemory:
    def __init__(self, max_turns=6):
        self.conversation_id = None
        self.max_turns = max_turns
        self.buffer = []

    def reset(self, conversation_id):
        self.conversation_id = conversation_id
        self.buffer = []

    def add(self, role, content):
        self.buffer.append((role, content))
        if len(self.buffer) > self.max_turns * 2:
            self.buffer = self.buffer[-self.max_turns * 2 :]

    def build_prompt(self, user_message: str) -> str:
        parts = []

        for role, content in self.buffer:
            # strip ALL role / inst tokens from memory
            clean = sanitize_prompt(content)
            parts.append(clean)

        # add current user message (sanitized)
        parts.append(sanitize_prompt(user_message))

        return "\n".join(parts)

