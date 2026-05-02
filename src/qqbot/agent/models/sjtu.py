import os

from openai import AsyncOpenAI

from qqbot.agent.models.base import ModelClient


class SJTUModelClient(ModelClient):
    def __init__(self):
        super().__init__("sjtu")
        self._model = os.getenv("SJTU_MODEL")
        base_url = os.getenv("SJTU_BASE_URL")
        api_key = os.getenv("SJTU_API_KEY")
        assert self._model and base_url and api_key
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    async def chat(self, messages: list[dict[str, str]]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        return (response.choices[0].message.content or "").strip()


def build_model_client() -> SJTUModelClient:
    return SJTUModelClient()
