import os
import sys
from dotenv import load_dotenv

import botpy
from botpy import logging
from botpy.message import GroupMessage, Message


logging = logging.get_logger()
REPLY_TEXT = "hello"


class HelloBot(botpy.Client):
    async def on_ready(self):
        logging.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        await message.reply(content=REPLY_TEXT)

    async def on_group_at_message_create(self, message: GroupMessage):
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=REPLY_TEXT,
        )


def read_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"缺少环境变量：{name}", file=sys.stderr)
        sys.exit(1)
    return value


if __name__ == "__main__":
    load_dotenv()
    appid = read_required_env("QQ_BOT_APPID")
    secret = read_required_env("QQ_BOT_SECRET")

    intents = botpy.Intents(
        public_guild_messages=True,
        public_messages=True,
    )
    client = HelloBot(intents=intents)
    client.run(appid=appid, secret=secret)
