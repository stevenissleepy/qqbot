from importlib import import_module
from pkgutil import iter_modules

from qqbot.agent import models
from qqbot.agent.models.base import ModelClient


def build_model_clients() -> dict[str, ModelClient]:
    clients: dict[str, ModelClient] = {}
    for module_info in iter_modules(models.__path__):
        if module_info.name.startswith("_") or module_info.name in {"base", "factory"}:
            continue

        module = import_module(f"{models.__name__}.{module_info.name}")
        factory = getattr(module, "build_model_client", None)
        if factory is None:
            continue

        client = factory()
        if client.name in clients:
            raise ValueError(f"重复模型名：{client.name}")
        clients[client.name] = client
    return clients
