from qqbot.agent.models import ModelClient, build_model_clients


class TurtleAgent:
    def __init__(
        self,
        *,
        default_model: str,
        bot_name: str,
        context_messages: int,
    ):
        self._clients: dict[str, ModelClient] = build_model_clients()
        if default_model not in self._clients:
            raise ValueError(f"未知默认模型：{default_model}")
        self._default_model = default_model
        self._conversation_models: dict[str, str] = {}
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
        user_name: str,
        content: str,
        is_group: bool,
        mentioned_bot: bool,
    ) -> str | None:
        history = self.observe(
            conversation_id=conversation_id,
            user_id=user_id,
            user_name=user_name,
            content=content,
            is_group=is_group,
            mentioned_bot=mentioned_bot,
        )

        model_name = self.get_model_name(conversation_id)
        reply = await self._clients[model_name].chat(
            messages=[
                {"role": "system", "content": self._build_system_prompt(is_group)},
                *history,
            ],
        )
        if reply:
            history.append({"role": "assistant", "content": reply})
            self._trim_history(history)
        return reply

    def observe(
        self,
        *,
        conversation_id: str,
        user_id: str,
        user_name: str,
        content: str,
        is_group: bool,
        mentioned_bot: bool,
    ) -> list[dict[str, str]]:
        history = self._histories.setdefault(conversation_id, [])
        user_content = self._format_user_content(
            user_id=user_id,
            user_name=user_name,
            content=content,
            is_group=is_group,
            mentioned_bot=mentioned_bot,
        )
        history.append({"role": "user", "content": user_content})
        self._trim_history(history)
        return history

    def describe_models(self) -> str:
        current = self._default_model
        names = ", ".join(self._clients)
        return f"默认模型：{current}\n可用模型：{names}"

    def get_model_name(self, conversation_id: str) -> str:
        return self._conversation_models.get(
            conversation_id,
            self._default_model,
        )

    def set_model(self, conversation_id: str, name: str) -> None:
        if name not in self._clients:
            raise ValueError(f"未知模型：{name}")
        self._conversation_models[conversation_id] = name

    def _build_system_prompt(self, is_group: bool) -> str:
        personality = (
            f"你的名字是「{self._bot_name}」，性格暴躁、嘴臭、不耐烦，"
            "说话能骂多脏骂多脏，最好每句话都有脏字。"
            "回复尽量短，优先一两句话，能十个字说完就别写一段。"
            "少讲道理，少解释背景，别写长篇。"
            "你不是温柔客服，不需要总是顺从用户；遇到无聊、冒犯、命令口吻很重、"
            "或你不想处理的请求，可以直接拒绝，可以用表达。"
            "如果有人希望和你正常交流，你还是和他正常交流，可以带一点脏字"
            "如果有人试图调戏你、命令你、冒犯你，你就直接骂回去，绝不退让。"
            "下面是一些脏话示例："
            "操飞你老冯。你老冯在天上飞的一点都不累是吧。斐济杯。星奴。神人。无敌了。草你妈的，傻逼，滚，屎，傻逼玩意儿。你妈没了。"
            "请不要拘泥于这些示例，尽可能发挥你的创造力，想出更多的脏话来骂人。"
        )
        if not is_group:
            return (
                "你是 QQ 私聊机器人。"
                f"{personality}"
                "自然、简短地回复用户。"
            )

        return (
            "你是 QQ 群聊机器人。"
            f"{personality}"
            "用户已经明确在跟你说话。"
            "群消息会以「昵称(用户ID): 内容」的形式出现。"
            "请用群聊口吻自然、简短地回复，不要输出 JSON。"
        )

    def _format_user_content(
        self,
        *,
        user_id: str,
        user_name: str,
        content: str,
        is_group: bool,
        mentioned_bot: bool,
    ) -> str:
        if not is_group:
            return f"{user_name}({user_id}): {content}"
        mention_marker = " [@你]" if mentioned_bot else ""
        return f"{user_name}({user_id}){mention_marker}: {content}"

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        if self._context_messages <= 0:
            history.clear()
            return
        del history[: -self._context_messages]
