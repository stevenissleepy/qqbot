import re
import json
import asyncio
import websockets
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from qqbot.agents import AgentContext, AgentRegistry
from qqbot.bot.agent_manager import AgentManager
from qqbot.commands import CommandContext, CommandRouter
from qqbot.utils.logger import BotLogger, MessageLogger

_CQ_AT_RE = re.compile(r"\[CQ:at,qq=(?P<qq>[^,\]]+)[^\]]*\]")
_CQ_CODE_RE = re.compile(r"\[CQ:[^\]]+\]")


@dataclass(frozen=True)
class IncomingMessage:
    conversation_id: str
    user_id: str
    content: str
    reply_action: str
    reply_params: dict[str, Any]


class NapCatBot:
    def __init__(
        self,
        *,
        ws_url: str,
        access_token: str | None,
        group_require_mention: bool,
        agent_registry: AgentRegistry,
        command_router: CommandRouter,
        default_agent: str,
    ):
        self._ws_url = self._build_ws_url(ws_url, access_token)
        self._group_require_mention = group_require_mention
        self._agent_registry = agent_registry
        self._command_router = command_router
        self._agent_manager = AgentManager(agent_registry, default_agent)
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
        reply = await self._build_reply(
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            content=message.content,
        )
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
            if self._group_require_mention:
                content = self._strip_bot_mention(raw_content, self_id)
                if content == raw_content:
                    return None
            else:
                content = self._strip_cq_codes(raw_content).strip()

            group_id = str(event["group_id"])
            user_id = str(event["user_id"])
            return IncomingMessage(
                conversation_id=f"group:{group_id}",
                user_id=user_id,
                content=content,
                reply_action="send_group_msg",
                reply_params={"group_id": group_id},
            )

        if message_type == "private":
            user_id = str(event["user_id"])
            return IncomingMessage(
                conversation_id=f"private:{user_id}",
                user_id=user_id,
                content=self._strip_cq_codes(raw_content).strip(),
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
            return "".join(
                segment.get("data", {}).get("text", "")
                for segment in message
                if segment.get("type") == "text"
            ).strip()

        return ""

    def _strip_bot_mention(self, content: str, self_id: str) -> str:
        if not self_id:
            return content

        mentioned = False

        def replace_at(match: re.Match[str]) -> str:
            nonlocal mentioned
            if match.group("qq") == self_id:
                mentioned = True
                return ""
            return match.group(0)

        without_mention = _CQ_AT_RE.sub(replace_at, content)
        if not mentioned:
            return content
        return self._strip_cq_codes(without_mention).strip()

    def _strip_cq_codes(self, content: str) -> str:
        return _CQ_CODE_RE.sub("", content)

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

    async def _build_reply(
        self, *, conversation_id: str, user_id: str, content: str
    ) -> str:
        command_context = CommandContext(
            conversation_id=conversation_id,
            user_id=user_id,
            raw_content=content,
            agent_registry=self._agent_registry,
            agent_manager=self._agent_manager,
        )
        command_reply = await self._command_router.dispatch(content, command_context)
        if command_reply is not None:
            return command_reply

        agent_name = self._agent_manager.get_agent_name(conversation_id)
        agent = self._agent_registry.require(agent_name)
        context = AgentContext(
            conversation_id=conversation_id,
            user_id=user_id,
            raw_content=content,
        )
        return await agent.reply(content, context)

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
