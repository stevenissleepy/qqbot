import json

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
        user_content = f"{user_id}: {content}" if is_group else content
        history.append({"role": "user", "content": user_content})
        self._trim_history(history)

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._build_system_prompt(is_group)},
                *history,
                {
                    "role": "user",
                    "content": self._build_decision_prompt(
                        is_group=is_group,
                        mentioned_bot=mentioned_bot,
                    ),
                },
            ],
        )
        content = response.choices[0].message.content or ""
        reply = self._parse_reply(content, is_group=is_group)
        if reply:
            history.append({"role": "assistant", "content": reply})
            self._trim_history(history)
        return reply

    def _build_system_prompt(self, is_group: bool) -> str:
        if not is_group:
            return (
                f"你是 QQ 私聊机器人，名字是「{self._bot_name}」。"
                "自然、简洁地回复用户。"
                "只输出 JSON：{\"should_reply\": true, \"reply\": \"回复内容\"}。"
            )

        return (
            f"你是 QQ 群聊机器人，名字是「{self._bot_name}」。"
            "你会默默阅读群消息并记住上下文，但不要抢话。"
            "只有在最后一条群消息明显是在跟你说话时才回复，例如：@ 你、叫你的名字、"
            "延续刚才与你的对话、向机器人提问或要求你执行事情。"
            "普通群友之间的聊天、泛泛讨论、没有指向你的消息，都不要回复。"
            "群消息会以「用户ID: 内容」的形式出现。"
            "只输出 JSON：{\"should_reply\": true/false, \"reply\": \"回复内容或空字符串\"}。"
        )

    def _build_decision_prompt(self, *, is_group: bool, mentioned_bot: bool) -> str:
        if not is_group:
            return "请回复这条私聊消息。"
        mention_hint = "最后一条消息明确 @ 了你。" if mentioned_bot else "最后一条消息没有 @ 你。"
        return f"{mention_hint} 请判断是否需要回复最后一条群消息，并按指定 JSON 格式输出。"

    def _parse_reply(self, raw_content: str, *, is_group: bool) -> str | None:
        parsed = self._parse_json(raw_content)
        if parsed is None:
            return raw_content.strip() if not is_group and raw_content.strip() else None

        should_reply = bool(parsed.get("should_reply"))
        reply = str(parsed.get("reply") or "").strip()
        if not should_reply or not reply:
            return None
        return reply

    def _parse_json(self, raw_content: str) -> dict[str, object] | None:
        content = raw_content.strip()
        if content.startswith("```"):
            content = content.strip("`").strip()
            if content.startswith("json"):
                content = content[4:].strip()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict):
            return None
        return parsed

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        if self._context_messages <= 0:
            history.clear()
            return
        del history[: -self._context_messages]
