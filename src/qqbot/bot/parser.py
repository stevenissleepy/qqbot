import re
from dataclasses import dataclass
from typing import Any


_CQ_AT_RE = re.compile(r"\[CQ:at,qq=(?P<qq>[^,\]]+)[^\]]*\]")
_CQ_CODE_RE = re.compile(r"\[CQ:[^\]]+\]")


@dataclass(frozen=True)
class IncomingMessage:
    conversation_id: str
    user_id: str
    user_name: str
    content: str
    is_group: bool
    mentioned_bot: bool
    reply_action: str
    reply_params: dict[str, Any]


class MessageParser:
    def __init__(self, *, agent_name: str):
        self._agent_name = agent_name

    def parse(self, event: dict[str, Any]) -> IncomingMessage | None:
        if event.get("post_type") != "message":
            return None

        message_type = event.get("message_type")
        raw_content = self._read_message_content(event)
        self_id = str(event.get("self_id", ""))

        if message_type == "group":
            mentioned_bot = self._mentions_bot(raw_content, self_id)
            content = self._normalize_message_content(raw_content, self_id).strip()

            group_id = str(event["group_id"])
            user_id = str(event["user_id"])
            user_name = self._read_sender_name(event, fallback=user_id)
            return IncomingMessage(
                conversation_id=f"group:{group_id}",
                user_id=user_id,
                user_name=user_name,
                content=content,
                is_group=True,
                mentioned_bot=mentioned_bot,
                reply_action="send_group_msg",
                reply_params={"group_id": group_id},
            )

        if message_type == "private":
            user_id = str(event["user_id"])
            user_name = self._read_sender_name(event, fallback=user_id)
            return IncomingMessage(
                conversation_id=f"private:{user_id}",
                user_id=user_id,
                user_name=user_name,
                content=self._normalize_message_content(raw_content, self_id).strip(),
                is_group=False,
                mentioned_bot=False,
                reply_action="send_private_msg",
                reply_params={"user_id": user_id},
            )

        return None

    def _read_message_content(self, event: dict[str, Any]) -> str:
        message = event.get("message")
        if isinstance(message, list):
            return "".join(
                self._message_segment_to_text(segment) for segment in message
            ).strip()

        if isinstance(message, str):
            return message.strip()

        raw_message = event.get("raw_message")
        if isinstance(raw_message, str):
            return raw_message.strip()

        return ""

    def _mentions_bot(self, content: str, self_id: str) -> bool:
        if not self_id:
            return False
        return any(
            match.group("qq") == self_id for match in _CQ_AT_RE.finditer(content)
        )

    def _normalize_message_content(self, content: str, self_id: str) -> str:
        def replace_at(match: re.Match[str]) -> str:
            qq = match.group("qq")
            if self_id and qq == self_id:
                return f"@{self._agent_name}"
            return f"@用户({qq})"

        return _CQ_CODE_RE.sub("", _CQ_AT_RE.sub(replace_at, content))

    def _message_segment_to_text(self, segment: dict[str, Any]) -> str:
        segment_type = segment.get("type")
        data = segment.get("data", {})
        if segment_type == "text":
            return str(data.get("text", ""))
        if segment_type == "at":
            qq = str(data.get("qq", ""))
            return f"[CQ:at,qq={qq}]"
        return ""

    def _read_sender_name(self, event: dict[str, Any], *, fallback: str) -> str:
        sender = event.get("sender")
        if not isinstance(sender, dict):
            return fallback

        for key in ("card", "nickname"):
            value = sender.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return fallback
