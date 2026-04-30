from qqbot.agents.base import Agent


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> Agent | None:
        return self._agents.get(name)

    def require(self, name: str) -> Agent:
        agent = self.get(name)
        if agent is None:
            available = ", ".join(self.names()) or "无"
            raise ValueError(f"未知 agent：{name}，可用 agent：{available}")
        return agent

    def names(self) -> list[str]:
        return sorted(self._agents)

    def describe(self) -> str:
        lines = []
        for name in self.names():
            agent = self._agents[name]
            lines.append(f"- {name}: {agent.description}")
        return "\n".join(lines)

