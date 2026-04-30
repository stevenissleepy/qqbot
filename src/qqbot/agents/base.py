from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AgentContext:
    conversation_id: str
    user_id: str
    raw_content: str


class Agent(Protocol):
    name: str
    description: str

    async def reply(self, message: str, context: AgentContext) -> str:
        """Return the text response for a QQ message."""
