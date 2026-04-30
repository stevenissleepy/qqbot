from dataclasses import dataclass
from typing import Protocol

from qqbot.agents import AgentRegistry
from qqbot.bot.agent_manager import AgentManager


@dataclass(frozen=True)
class CommandContext:
    conversation_id: str
    user_id: str
    raw_content: str
    agent_registry: AgentRegistry
    agent_manager: AgentManager


class Command(Protocol):
    name: str
    description: str

    async def handle(self, args: list[str], context: CommandContext) -> str:
        """Return the command response."""
