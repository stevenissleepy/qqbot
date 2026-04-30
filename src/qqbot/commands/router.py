from dataclasses import dataclass

from qqbot.commands.base import CommandContext
from qqbot.commands.registry import CommandRegistry


@dataclass(frozen=True)
class ParsedCommand:
    name: str
    args: list[str]


class CommandRouter:
    def __init__(self, registry: CommandRegistry):
        self._registry = registry

    async def dispatch(self, content: str, context: CommandContext) -> str | None:
        parsed = self._parse(content)
        if parsed is None:
            return None

        command = self._registry.get(parsed.name)
        if command is None:
            return f"未知命令：/{parsed.name}"
        return await command.handle(parsed.args, context)

    def _parse(self, content: str) -> ParsedCommand | None:
        parts = content.strip().split()
        command_index = next(
            (index for index, part in enumerate(parts) if part.startswith("/") and len(part) > 1),
            None,
        )
        if command_index is None:
            return None

        command_name = parts[command_index][1:]
        return ParsedCommand(name=command_name, args=parts[command_index + 1 :])
