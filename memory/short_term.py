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

    def build_prompt(self, user_message: str):
        parts = []
        for role, content in self.buffer:
            if role == "user":
                parts.append(f"[USER] {content}")
            else:
                parts.append(f"[ASSISTANT] {content}")
        parts.append(f"[USER] {user_message}")
        return "\n".join(parts)
