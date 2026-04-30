from qqbot.agents import AgentRegistry


class AgentManager:
    def __init__(self, registry: AgentRegistry, default_agent: str):
        self._registry = registry
        self._default_agent = default_agent
        self._conversation_agents: dict[str, str] = {}

    def get_agent_name(self, conversation_id: str) -> str:
        return self._conversation_agents.get(conversation_id, self._default_agent)

    def set_agent(self, conversation_id: str, agent_name: str) -> None:
        self._registry.require(agent_name)
        self._conversation_agents[conversation_id] = agent_name

