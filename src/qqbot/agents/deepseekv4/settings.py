import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DeepSeekSettings:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls) -> "DeepSeekSettings":
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        )
