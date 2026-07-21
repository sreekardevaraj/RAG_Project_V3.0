from config.settings import MAX_MEMORY_MESSAGES


class ChatMemory:
    """Stores last N messages and returns them as a formatted string for LLM context."""

    def __init__(self):
        self.messages = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > MAX_MEMORY_MESSAGES:
            self.messages = self.messages[-MAX_MEMORY_MESSAGES:]

    def get_history_string(self) -> str:
        if not self.messages:
            return "No previous conversation."
        lines = []
        for msg in self.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def clear(self):
        self.messages = []

    def get_messages(self) -> list:
        return self.messages