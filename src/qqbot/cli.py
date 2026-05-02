from dotenv import load_dotenv

from qqbot.agent import TurtleAgent
from qqbot.bot.client import NapCatBot
from qqbot.config import load_settings


def main() -> None:
    load_dotenv()
    settings = load_settings()
    agent = TurtleAgent(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        bot_name=settings.agent_name,
        context_messages=settings.context_messages,
    )

    client = NapCatBot(
        ws_url=settings.napcat_ws_url,
        access_token=settings.napcat_access_token,
        agent=agent,
    )
    client.run()
