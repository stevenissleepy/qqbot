from dotenv import load_dotenv

from qqbot.agents import build_default_registry
from qqbot.bot.client import NapCatBot
from qqbot.commands import AgentCommand, CommandRegistry, CommandRouter
from qqbot.config import load_settings


def main() -> None:
    load_dotenv()
    settings = load_settings()
    agent_registry = build_default_registry()
    agent_registry.require(settings.default_agent)

    command_registry = CommandRegistry()
    command_registry.register(AgentCommand())
    command_router = CommandRouter(command_registry)

    client = NapCatBot(
        ws_url=settings.napcat_ws_url,
        access_token=settings.napcat_access_token,
        group_require_mention=settings.group_require_mention,
        agent_registry=agent_registry,
        command_router=command_router,
        default_agent=settings.default_agent,
    )
    client.run()
