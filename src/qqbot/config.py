import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    napcat_ws_url: str
    napcat_access_token: str | None
    agent_name: str
    default_model: str
    context_messages: int


def read_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        print(f"环境变量 {name} 必须是整数", file=sys.stderr)
        sys.exit(1)


def load_settings() -> Settings:
    return Settings(
        napcat_ws_url=os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:3001"),
        napcat_access_token=os.getenv("NAPCAT_ACCESS_TOKEN") or None,
        agent_name=os.getenv("AGENT_NAME", "龟龟"),
        default_model=os.getenv("AGENT_DEFAULT_MODEL", "sjtu"),
        context_messages=read_int_env("AGENT_CONTEXT_MESSAGES", 20),
    )
