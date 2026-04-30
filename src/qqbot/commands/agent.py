from qqbot.commands.base import CommandContext


class AgentCommand:
    name = "agent"
    description = "查看或切换当前会话使用的 agent"

    async def handle(self, args: list[str], context: CommandContext) -> str:
        if len(args) == 1 and args[0] == "list":
            current = context.agent_manager.get_agent_name(context.conversation_id)
            return f"当前 agent：{current}\n可用 agent：\n{context.agent_registry.describe()}"

        if len(args) != 1:
            return "用法：/agent list 或 /agent <name>"

        agent_name = args[0]
        try:
            context.agent_manager.set_agent(context.conversation_id, agent_name)
        except ValueError as exc:
            return str(exc)
        return f"已切换到 agent：{agent_name}"
