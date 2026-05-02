from qqbot.agent.models import ModelClient, build_model_clients
from qqbot.agent.personas import Persona, build_personas


class TurtleAgent:
    def __init__(
        self,
        *,
        default_model: str,
        default_persona: str,
        bot_name: str,
        context_messages: int,
    ):
        self._clients: dict[str, ModelClient] = build_model_clients()
        if default_model not in self._clients:
            raise ValueError(f"未知默认模型：{default_model}")
        self._personas: dict[str, Persona] = build_personas()
        if default_persona not in self._personas:
            raise ValueError(f"未知默认 persona：{default_persona}")
        self._default_model = default_model
        self._default_persona = default_persona
        self._conversation_models: dict[str, str] = {}
        self._conversation_personas: dict[str, str] = {}
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
                {
                    "role": "system",
                    "content": self._build_system_prompt(
                        conversation_id=conversation_id,
                        is_group=is_group,
                    ),
                },
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

    def describe_personas(self) -> str:
        current = self._default_persona
        names = ", ".join(self._personas)
        return f"默认 persona：{current}\n可用 persona：{names}"

    def get_persona_name(self, conversation_id: str) -> str:
        return self._conversation_personas.get(
            conversation_id,
            self._default_persona,
        )

    def set_persona(self, conversation_id: str, name: str) -> None:
        if name not in self._personas:
            raise ValueError(f"未知 persona：{name}")
        self._conversation_personas[conversation_id] = name

    def _build_system_prompt(self, *, conversation_id: str, is_group: bool) -> str:
        persona_name = self.get_persona_name(conversation_id)
        return self._personas[persona_name].build_system_prompt(
            bot_name=self._bot_name,
            is_group=is_group,
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
        speaker = f"{user_name}({user_id})"
        if not is_group:
            return f"[{speaker}] {content}"
        mention_marker = " @你" if mentioned_bot else ""
        return f"[{speaker}{mention_marker}] {content}"

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        if self._context_messages <= 0:
            history.clear()
            return
        del history[: -self._context_messages]
