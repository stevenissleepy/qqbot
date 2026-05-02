import os
from dotenv import load_dotenv

from qqbot.agent.turtle_agent import TurtleAgent
from qqbot.bot.client import NapCatBot


def main() -> None:
    load_dotenv()
    agent = TurtleAgent(
        bot_name=os.getenv("AGENT_NAME", "龟龟"),
        default_model=os.getenv("AGENT_DEFAULT_MODEL", "sjtu"),
        default_persona=os.getenv("AGENT_DEFAULT_PERSONA", "mean"),
        context_messages=int(os.getenv("AGENT_CONTEXT_MESSAGES", 20)),
    )

    client = NapCatBot(
        ws_url=os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:3001"),
        access_token=os.getenv("NAPCAT_ACCESS_TOKEN") or None,
        agent=agent,
    )
    client.run()


if __name__ == "__main__":
    main()
