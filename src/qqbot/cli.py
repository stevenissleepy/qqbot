from dotenv import load_dotenv

import botpy

from qqbot.agents import build_default_registry
from qqbot.bot.client import QQBot
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

    intents = botpy.Intents(
        public_guild_messages=True,
        public_messages=True,
    )
    client = QQBot(
        intents=intents,
        agent_registry=agent_registry,
        command_router=command_router,
        default_agent=settings.default_agent,
    )
    client.run(appid=settings.appid, secret=settings.secret)
