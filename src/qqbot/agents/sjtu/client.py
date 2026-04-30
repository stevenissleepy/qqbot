from openai import APIStatusError, AsyncOpenAI, OpenAIError

from qqbot.agents.sjtu.settings import SJTUSettings


class SJTUClient:
    def __init__(self, settings: SJTUSettings):
        self._settings = settings

    async def chat(self, message: str) -> str:
        client = AsyncOpenAI(
            api_key=self._settings.api_key,
            base_url=self._settings.base_url,
        )
        try:
            response = await client.chat.completions.create(
                model=self._settings.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ],
                stream=False,
            )
        except APIStatusError as exc:
            return f"SJTU API 请求失败：HTTP {exc.status_code}，请检查 SJTU_BASE_URL 和 SJTU_MODEL"
        except OpenAIError as exc:
            return f"SJTU API 请求失败：{exc}"
        reply = response.choices[0].message.content
        return reply or "SJTU 没有返回内容"
