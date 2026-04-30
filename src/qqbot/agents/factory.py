from qqbot.agents.builtin import BuiltinAgent
from qqbot.agents.deepseek import DeepSeekAgent
from qqbot.agents.registry import AgentRegistry
from qqbot.agents.sjtu import SJTUAgent


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(BuiltinAgent())
    registry.register(DeepSeekAgent())
    registry.register(SJTUAgent())
    return registry
