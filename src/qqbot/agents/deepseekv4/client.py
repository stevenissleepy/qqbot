from openai import AsyncOpenAI

from qqbot.agents.deepseekv4.settings import DeepSeekSettings


class DeepSeekClient:
    def __init__(self, settings: DeepSeekSettings):
        self._settings = settings

    async def chat(self, message: str) -> str:
        client = AsyncOpenAI(
            api_key=self._settings.api_key,
            base_url=self._settings.base_url,
        )
        response = await client.chat.completions.create(
            model=self._settings.model,
            messages=[
                {"role": "user", "content": message},
            ],
        )
        reply = response.choices[0].message.content
        return reply or "DeepSeek 没有返回内容"
