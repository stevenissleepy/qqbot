from qqbot.agent.turtle_agent import TurtleAgent
from qqbot.bot.parser import IncomingMessage


class CommandHandler:
    def __init__(self, agent: TurtleAgent):
        self._agent = agent

    def handle(self, message: IncomingMessage) -> str | None:
        parts = message.content.strip().split()
        command_index = next(
            (
                index
                for index, part in enumerate(parts)
                if part in {"/help", "/model", "/persona", "/context"}
            ),
            None,
        )
        if command_index is None:
            return None

        command = parts[command_index]
        args = parts[command_index + 1 :]
        if command == "/help":
            return self._handle_help_command()
        if command == "/model":
            return self._handle_model_command(message, args)
        if command == "/persona":
            return self._handle_persona_command(message, args)
        if command == "/context":
            return self._handle_context_command(message, args)
        return None

    def _handle_help_command(self) -> str:
        return (
            "目前所有可用指令：\n"
            "[/model]\n"
            "/model list : 列出所有可用 model\n"
            "/model {name} : 切换到 {name}\n\n"
            "[/persona]\n"
            "/persona list :  列出所有可用人格\n"
            "/persona {name} : 切换到 {name}\n\n"
            "[/context]\n"
            "/context clear : 清空当前会话上下文"
        )

    def _handle_model_command(self, message: IncomingMessage, args: list[str]) -> str:
        if not args:
            current = self._agent.get_model_name(message.conversation_id)
            return f"当前模型：{current}\n{self._agent.describe_models()}"

        if len(args) == 1 and args[0] == "list":
            current = self._agent.get_model_name(message.conversation_id)
            return f"当前模型：{current}\n{self._agent.describe_models()}"

        if len(args) != 1:
            return "用法：/model list 或 /model <name>"

        model_name = args[0]
        try:
            self._agent.set_model(message.conversation_id, model_name)
        except ValueError as exc:
            return str(exc)
        return f"已切换模型：{model_name}"

    def _handle_persona_command(self, message: IncomingMessage, args: list[str]) -> str:
        if not args:
            current = self._agent.get_persona_name(message.conversation_id)
            return f"当前 persona：{current}\n{self._agent.describe_personas()}"

        if len(args) == 1 and args[0] == "list":
            current = self._agent.get_persona_name(message.conversation_id)
            return f"当前 persona：{current}\n{self._agent.describe_personas()}"

        if len(args) != 1:
            return "用法：/persona list 或 /persona <name>"

        persona_name = args[0]
        try:
            self._agent.set_persona(message.conversation_id, persona_name)
        except ValueError as exc:
            return str(exc)
        return f"已切换 persona：{persona_name}"

    def _handle_context_command(self, message: IncomingMessage, args: list[str]) -> str:
        if len(args) == 1 and args[0] == "clear":
            self._agent.clear_context(message.conversation_id)
            return "已清空当前会话上下文"
        return "用法：/context clear"
