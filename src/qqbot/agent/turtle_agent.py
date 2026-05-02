from openai import AsyncOpenAI


class TurtleAgent:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        bot_name: str,
        context_messages: int,
    ):
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self._model = model
        self._bot_name = bot_name
        self._context_messages = context_messages
        self._histories: dict[str, list[dict[str, str]]] = {}

    @property
    def name(self) -> str:
        return self._bot_name

    async def observe_and_reply(
        self,
        *,
        conversation_id: str,
        user_id: str,
        content: str,
        is_group: bool,
        mentioned_bot: bool,
    ) -> str | None:
        history = self._histories.setdefault(conversation_id, [])
        user_content = self._format_user_content(
            user_id=user_id,
            content=content,
            is_group=is_group,
            mentioned_bot=mentioned_bot,
        )
        history.append({"role": "user", "content": user_content})
        self._trim_history(history)

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._build_system_prompt(is_group)},
                *history,
            ],
        )
        content = response.choices[0].message.content or ""
        reply = content.strip()
        if reply:
            history.append({"role": "assistant", "content": reply})
            self._trim_history(history)
        return reply

    def _build_system_prompt(self, is_group: bool) -> str:
        if not is_group:
            return (
                f"你是 QQ 私聊机器人，名字是「{self._bot_name}」。"
                "自然、简洁地回复用户。"
            )

        return (
            f"你是 QQ 群聊机器人，名字是「{self._bot_name}」。"
            "用户已经明确在跟你说话。"
            "群消息会以「用户ID: 内容」的形式出现。"
            "请自然、简洁地回复，不要输出 JSON。"
        )

    def _format_user_content(
        self,
        *,
        user_id: str,
        content: str,
        is_group: bool,
        mentioned_bot: bool,
    ) -> str:
        if not is_group:
            return content
        mention_marker = " [@你]" if mentioned_bot else ""
        return f"{user_id}{mention_marker}: {content}"

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        if self._context_messages <= 0:
            history.clear()
            return
        del history[: -self._context_messages]
