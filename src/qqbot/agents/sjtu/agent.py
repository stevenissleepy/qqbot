from qqbot.agents.base import AgentContext
from qqbot.agents.sjtu.client import SJTUClient
from qqbot.agents.sjtu.settings import SJTUSettings


class SJTUAgent:
    name = "sjtu"
    description = "使用 SJTU API 进行最简单的单轮聊天"

    async def reply(self, message: str, context: AgentContext) -> str:
        content = message.strip()
        if not content:
            return "你想聊点什么？"

        settings = SJTUSettings.from_env()
        if not settings.api_key:
            return "缺少环境变量：SJTU_API_KEY"

        client = SJTUClient(settings)
        return await client.chat(content)

