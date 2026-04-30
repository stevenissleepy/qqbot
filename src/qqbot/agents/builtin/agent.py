from qqbot.agents.base import AgentContext


class BuiltinAgent:
    name = "builtin"
    description = "内置示例 agent，固定回复 hello"

    async def reply(self, message: str, context: AgentContext) -> str:
        return "hello"

