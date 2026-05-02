import re
import json
import asyncio
import websockets
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from qqbot.agent import TurtleAgent
from qqbot.utils.logger import BotLogger, MessageLogger

_CQ_AT_RE = re.compile(r"\[CQ:at,qq=(?P<qq>[^,\]]+)[^\]]*\]")
_CQ_CODE_RE = re.compile(r"\[CQ:[^\]]+\]")


@dataclass(frozen=True)
class IncomingMessage:
    conversation_id: str
    user_id: str
    content: str
    is_group: bool
    mentioned_bot: bool
    reply_action: str
    reply_params: dict[str, Any]


class NapCatBot:
    def __init__(
        self,
        *,
        ws_url: str,
        access_token: str | None,
        agent: TurtleAgent,
    ):
        self._ws_url = self._build_ws_url(ws_url, access_token)
        self._agent = agent
        self._agent_name = agent.name
        self._bot_logger = BotLogger()
        self._message_logger = MessageLogger()

    def run(self) -> None:
        asyncio.run(self._run_forever())

    async def _run_forever(self) -> None:
        while True:
            try:
                await self._connect_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                self._bot_logger.exception(
                    "NapCat WebSocket disconnected, retrying in 5s"
                )
                await asyncio.sleep(5)

    async def _connect_once(self) -> None:
        async with websockets.connect(self._ws_url) as websocket:
            self._bot_logger.info("connected to NapCat WebSocket: %s", self._ws_url)
            async for raw_event in websocket:
                await self._handle_raw_event(websocket, raw_event)

    async def _handle_raw_event(self, websocket: Any, raw_event: str | bytes) -> None:
        try:
            event = json.loads(raw_event)
        except json.JSONDecodeError:
            self._bot_logger.warning("received non-json event from NapCat")
            return

        message = self._parse_message_event(event)
        if message is None:
            return

        self._log_message_received(
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            content=message.content,
        )
        if not self._should_reply(message):
            return

        reply = await self._agent.observe_and_reply(
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            content=message.content,
            is_group=message.is_group,
            mentioned_bot=message.mentioned_bot,
        )
        if reply is None:
            return

        self._log_message_reply(
            conversation_id=message.conversation_id,
            content=reply,
        )
        await self._send_action(
            websocket,
            message.reply_action,
            {
                **message.reply_params,
                "message": reply,
            },
        )

    def _parse_message_event(self, event: dict[str, Any]) -> IncomingMessage | None:
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
            return IncomingMessage(
                conversation_id=f"group:{group_id}",
                user_id=user_id,
                content=content,
                is_group=True,
                mentioned_bot=mentioned_bot,
                reply_action="send_group_msg",
                reply_params={"group_id": group_id},
            )

        if message_type == "private":
            user_id = str(event["user_id"])
            return IncomingMessage(
                conversation_id=f"private:{user_id}",
                user_id=user_id,
                content=self._normalize_message_content(raw_content, self_id).strip(),
                is_group=False,
                mentioned_bot=False,
                reply_action="send_private_msg",
                reply_params={"user_id": user_id},
            )

        return None

    def _read_message_content(self, event: dict[str, Any]) -> str:
        raw_message = event.get("raw_message")
        if isinstance(raw_message, str):
            return raw_message.strip()

        message = event.get("message")
        if isinstance(message, str):
            return message.strip()

        if isinstance(message, list):
            return "".join(self._message_segment_to_text(segment) for segment in message).strip()

        return ""

    def _mentions_bot(self, content: str, self_id: str) -> bool:
        if not self_id:
            return False
        return any(match.group("qq") == self_id for match in _CQ_AT_RE.finditer(content))

    def _should_reply(self, message: IncomingMessage) -> bool:
        if not message.is_group:
            return True
        return message.mentioned_bot or self._agent_name in message.content

    def _normalize_message_content(self, content: str, self_id: str) -> str:
        def replace_at(match: re.Match[str]) -> str:
            if self_id and match.group("qq") == self_id:
                return f"@{self._agent_name}"
            return "@某人"

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

    async def _send_action(
        self,
        websocket: Any,
        action: str,
        params: dict[str, Any],
    ) -> None:
        await websocket.send(
            json.dumps(
                {
                    "action": action,
                    "params": params,
                },
                ensure_ascii=False,
            )
        )

    def _log_message_received(
        self, *, conversation_id: str, user_id: str, content: str
    ) -> None:
        self._message_logger.received(
            conversation_id=conversation_id,
            user_id=user_id,
            content=content,
        )

    def _log_message_reply(self, *, conversation_id: str, content: str) -> None:
        self._message_logger.reply(
            conversation_id=conversation_id,
            content=content,
        )

    def _build_ws_url(self, ws_url: str, access_token: str | None) -> str:
        if not access_token:
            return ws_url

        parts = urlsplit(ws_url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query.setdefault("access_token", access_token)
        return urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                urlencode(query),
                parts.fragment,
            )
        )
