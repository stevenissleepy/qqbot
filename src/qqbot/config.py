import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    napcat_ws_url: str
    napcat_access_token: str | None
    openai_base_url: str
    openai_api_key: str
    openai_model: str
    agent_name: str
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


def read_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"缺少环境变量：{name}", file=sys.stderr)
        sys.exit(1)
    return value


def load_settings() -> Settings:
    return Settings(
        napcat_ws_url=os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:3001"),
        napcat_access_token=os.getenv("NAPCAT_ACCESS_TOKEN") or None,
        openai_base_url=read_required_env("OPENAI_BASE_URL"),
        openai_api_key=read_required_env("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
        agent_name=os.getenv("AGENT_NAME", "龟龟"),
        context_messages=read_int_env("AGENT_CONTEXT_MESSAGES", 20),
    )
