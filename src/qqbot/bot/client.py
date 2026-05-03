import asyncio
import json
from contextlib import suppress
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import websockets

from qqbot.agent.turtle_agent import TurtleAgent
from qqbot.bot.commands import CommandHandler
from qqbot.bot.member_cache import GroupMemberCache
from qqbot.bot.onebot import OneBotApi
from qqbot.bot.parser import MessageParser
from qqbot.utils.logger import BotLogger, MessageLogger


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
        self._bot_logger = BotLogger()
        self._message_logger = MessageLogger()
        self._onebot = OneBotApi()
        self._parser = MessageParser(agent_name=agent.name)
        self._commands = CommandHandler(agent)
        self._member_cache = GroupMemberCache(
            onebot=self._onebot,
            logger=self._bot_logger,
        )

    def run(self) -> None:
        try:
            asyncio.run(self._run_forever())
        except KeyboardInterrupt:
            pass

    async def _run_forever(self) -> None:
        while True:
            try:
                await self._connect_once()
            except asyncio.CancelledError:
                self._bot_logger.info("shutting down NapCat bot")
                raise
            except Exception:
                self._bot_logger.exception(
                    "NapCat WebSocket disconnected, retrying in 5s"
                )
                await asyncio.sleep(5)

    async def _connect_once(self) -> None:
        async with websockets.connect(self._ws_url) as websocket:
            self._bot_logger.info("connected to NapCat WebSocket: %s", self._ws_url)
            event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
            receiver = asyncio.create_task(self._receive_events(websocket, event_queue))
            try:
                while True:
                    event = await event_queue.get()
                    await self._handle_event(websocket, event)
            finally:
                receiver.cancel()
                with suppress(asyncio.CancelledError):
                    await receiver

    async def _receive_events(
        self,
        websocket: Any,
        event_queue: asyncio.Queue[dict[str, Any]],
    ) -> None:
        async for raw_event in websocket:
            try:
                event = json.loads(raw_event)
            except json.JSONDecodeError:
                self._bot_logger.warning("received non-json event from NapCat")
                continue

            if self._onebot.handle_response(event):
                continue

            await event_queue.put(event)

    async def _handle_raw_event(self, websocket: Any, raw_event: str | bytes) -> None:
        try:
            event = json.loads(raw_event)
        except json.JSONDecodeError:
            self._bot_logger.warning("received non-json event from NapCat")
            return

        await self._handle_event(websocket, event)

    async def _handle_event(self, websocket: Any, event: dict[str, Any]) -> None:
        message = self._parser.parse(event)
        if message is None:
            return

        if message.is_group:
            message = await self._member_cache.hydrate_mentions(websocket, message)

        self._log_message_received(
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            content=message.content,
        )
        if not self._should_reply(message):
            self._agent.observe(
                conversation_id=message.conversation_id,
                user_id=message.user_id,
                user_name=message.user_name,
                content=message.content,
                is_group=message.is_group,
                mentioned_bot=message.mentioned_bot,
            )
            return

        command_reply = self._commands.handle(message)
        if command_reply is not None:
            await self._reply(websocket, message, command_reply)
            return

        reply = await self._agent.observe_and_reply(
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            user_name=message.user_name,
            content=message.content,
            is_group=message.is_group,
            mentioned_bot=message.mentioned_bot,
        )
        if reply is not None:
            await self._reply(websocket, message, reply)

    def _should_reply(self, message: Any) -> bool:
        if not message.is_group:
            return True
        return message.mentioned_bot or self._agent.name in message.content

    async def _reply(self, websocket: Any, message: Any, content: str) -> None:
        self._log_message_reply(
            conversation_id=message.conversation_id,
            content=content,
        )
        await self._onebot.send_action(
            websocket,
            message.reply_action,
            {
                **message.reply_params,
                "message": content,
            },
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
