import os
from dataclasses import dataclass

DEFAULT_SJTU_BASE_URL = "https://models.sjtu.edu.cn/api/v1"
DEFAULT_SJTU_MODEL = "deepseek-chat"


@dataclass(frozen=True)
class SJTUSettings:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls) -> "SJTUSettings":
        return cls(
            api_key=os.getenv("SJTU_API_KEY", ""),
            base_url=os.getenv("SJTU_BASE_URL", DEFAULT_SJTU_BASE_URL),
            model=os.getenv("SJTU_MODEL", DEFAULT_SJTU_MODEL),
        )
