import logging as py_logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from botpy import logging as botpy_logging


class BotLogger:
    _DEFAULT_LOG_DIR = "log"
    _DEFAULT_LOG_FILE = "bot.log"

    def __init__(self):
        log_dir = self._read_log_dir()
        log_file = log_dir / os.getenv("BOT_LOG_FILE", self._DEFAULT_LOG_FILE)
        log_level = self._read_log_level()

        botpy_logging.configure_logging(
            level=log_level,
            bot_log=True,
            ext_handlers={
                "handler": TimedRotatingFileHandler,
                "level": py_logging.DEBUG,
                "when": "D",
                "backupCount": 7,
                "encoding": "utf-8",
                "filename": str(log_file),
            },
            force=True,
        )
        self._logger = botpy_logging.get_logger()

    def info(self, msg: object, *args: object, **kwargs: object) -> None:
        kwargs.setdefault("stacklevel", 2)
        self._logger.info(msg, *args, **kwargs)

    def __getattr__(self, name: str) -> object:
        return getattr(self._logger, name)

    def _read_log_dir(self) -> Path:
        log_dir = Path(os.getenv("BOT_LOG_DIR", self._DEFAULT_LOG_DIR))
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def _read_log_level(self) -> int:
        level_name = os.getenv("BOT_LOG_LEVEL", "INFO").upper()
        return getattr(py_logging, level_name, py_logging.INFO)


class MessageLogger:
    _DEFAULT_LOG_DIR = "log"
    _DEFAULT_LOG_FILE = "message.log"
    _DEFAULT_MAX_LENGTH = 500
    _ACTION_WIDTH = len("received")
    _FILE_FORMAT = "%(asctime)s\t%(message)s"
    _LOGGER_NAME = "qqbot.message"

    def __init__(self):
        log_dir = Path(os.getenv("MESSAGE_LOG_DIR", self._DEFAULT_LOG_DIR))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / os.getenv("MESSAGE_LOG_FILE", self._DEFAULT_LOG_FILE)
        log_level = getattr(
            py_logging, os.getenv("BOT_LOG_LEVEL", "INFO").upper(), py_logging.INFO
        )
        self._max_length = int(
            os.getenv("MESSAGE_LOG_MAX_LENGTH", self._DEFAULT_MAX_LENGTH)
        )

        self._logger = py_logging.getLogger(self._LOGGER_NAME)
        self._logger.handlers.clear()
        self._logger.setLevel(log_level)
        self._logger.propagate = False

        file_handler = py_logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(py_logging.Formatter(self._FILE_FORMAT))
        self._logger.addHandler(file_handler)

    def received(self, *, conversation_id: str, user_id: str, content: str) -> None:
        action = "received".ljust(self._ACTION_WIDTH)
        prefix = f"[{conversation_id}] {action}  "
        content = f"{user_id}: {self._truncate(content, self._max_length)}"
        self._log(prefix=prefix, content=content)

    def reply(self, *, conversation_id: str, content: str) -> None:
        action = "reply".ljust(self._ACTION_WIDTH)
        prefix = f"[{conversation_id}] {action}  "
        content = self._truncate(content, self._max_length)
        self._log(prefix=prefix, content=content)

    def __getattr__(self, name: str) -> object:
        return getattr(self._logger, name)

    def _log(self, *, prefix: str, content: str) -> None:
        self._logger.info("%s%s", prefix, content)
        sys.stderr.write(f"\033[33m{prefix}\033[0m{content}\n")

    def _truncate(self, value: str, max_length: int) -> str:
        normalized = value.replace("\r", "\\r").replace("\n", "\\n")
        if max_length <= 0 or len(normalized) <= max_length:
            return normalized
        return f"{normalized[:max_length]}..."
