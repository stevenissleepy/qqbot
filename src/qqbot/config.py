import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    appid: str
    secret: str
    default_agent: str


def read_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"缺少环境变量：{name}", file=sys.stderr)
        sys.exit(1)
    return value


def load_settings() -> Settings:
    return Settings(
        appid=read_required_env("QQ_BOT_APPID"),
        secret=read_required_env("QQ_BOT_SECRET"),
        default_agent=os.getenv("QQ_BOT_AGENT", "builtin"),
    )
