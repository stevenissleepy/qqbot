import asyncio
import json
import uuid
from typing import Any


class OneBotApi:
    def __init__(self):
        self._pending_actions: dict[str, asyncio.Future[dict[str, Any]]] = {}

    def handle_response(self, event: dict[str, Any]) -> bool:
        echo = event.get("echo")
        if not isinstance(echo, str) or echo not in self._pending_actions:
            return False

        future = self._pending_actions.pop(echo)
        if not future.done():
            future.set_result(event)
        return True

    async def send_action(
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

    async def call_action(
        self,
        websocket: Any,
        action: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        echo = f"{action}:{uuid.uuid4()}"
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_actions[echo] = future
        await websocket.send(
            json.dumps(
                {
                    "action": action,
                    "params": params,
                    "echo": echo,
                },
                ensure_ascii=False,
            )
        )
        try:
            return await asyncio.wait_for(future, timeout=5)
        finally:
            self._pending_actions.pop(echo, None)
