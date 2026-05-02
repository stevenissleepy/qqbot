import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    napcat_ws_url: str
    napcat_access_token: str | None
    group_require_mention: bool
    default_agent: str


def read_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    return Settings(
        napcat_ws_url=os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:3001"),
        napcat_access_token=os.getenv("NAPCAT_ACCESS_TOKEN") or None,
        group_require_mention=read_bool_env("NAPCAT_GROUP_REQUIRE_MENTION", True),
        default_agent=os.getenv("QQ_BOT_AGENT", "builtin"),
    )
