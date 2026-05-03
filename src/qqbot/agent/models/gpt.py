import os

from openai import AsyncOpenAI

from qqbot.agent.models.base import ModelClient


class GPTModelClient(ModelClient):
    def __init__(self):
        super().__init__("gpt")
        self._model = os.getenv("GPT_MODEL")
        api_key = os.getenv("GPT_API_KEY")
        base_url = os.getenv("GPT_BASE_URL")
        assert self._model and api_key

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = AsyncOpenAI(**kwargs)

    async def chat(self, messages: list[dict[str, str]]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        return (response.choices[0].message.content or "").strip()


def build_model_client() -> GPTModelClient | None:
    if not os.getenv("GPT_API_KEY") or not os.getenv("GPT_MODEL"):
        return None
    return GPTModelClient()
