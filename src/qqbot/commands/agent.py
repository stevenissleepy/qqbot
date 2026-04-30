from qqbot.commands.base import CommandContext


class AgentCommand:
    name = "agent"
    description = "查看或切换当前会话使用的 agent"

    async def handle(self, args: list[str], context: CommandContext) -> str:
        if not args or args[0] in {"list", "ls"}:
            current = context.agent_manager.get_agent_name(context.conversation_id)
            return f"当前 agent：{current}\n可用 agent：\n{context.agent_registry.describe()}"

        if args[0] in {"use", "set"}:
            if len(args) < 2:
                return "用法：/agent use <name>"
            agent_name = args[1]
        else:
            agent_name = args[0]

        try:
            context.agent_manager.set_agent(context.conversation_id, agent_name)
        except ValueError as exc:
            return str(exc)
        return f"已切换到 agent：{agent_name}"

