from qqbot.agents.base import AgentContext
from qqbot.agents.deepseek.client import DeepSeekClient
from qqbot.agents.deepseek.settings import DeepSeekSettings


class DeepSeekAgent:
    name = "deepseek"
    description = "使用 DeepSeek API 进行最简单的单轮聊天"

    async def reply(self, message: str, context: AgentContext) -> str:
        content = message.strip()
        if not content:
            return "你想聊点什么？"

        settings = DeepSeekSettings.from_env()
        if not settings.api_key:
            return "缺少环境变量：DEEPSEEK_API_KEY"

        client = DeepSeekClient(settings)
        return await client.chat(content)
