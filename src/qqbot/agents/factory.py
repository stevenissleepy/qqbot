from qqbot.agents.builtin import BuiltinAgent
from qqbot.agents.deepseekv4 import DeepSeekV4Agent
from qqbot.agents.registry import AgentRegistry


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(BuiltinAgent())
    registry.register(DeepSeekV4Agent())
    return registry
