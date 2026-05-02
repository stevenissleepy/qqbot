import re
from typing import Any

from qqbot.bot.onebot import OneBotApi
from qqbot.bot.parser import IncomingMessage


class GroupMemberCache:
    def __init__(self, *, onebot: OneBotApi, logger: Any):
        self._onebot = onebot
        self._logger = logger
        self._member_name_cache: dict[tuple[str, str], str] = {}

    async def hydrate_mentions(
        self,
        websocket: Any,
        message: IncomingMessage,
    ) -> IncomingMessage:
        group_id = str(message.reply_params.get("group_id", ""))
        if not group_id:
            return message

        hydrated_content = message.content
        for match in list(re.finditer(r"@用户\((?P<user_id>\d+)\)", message.content)):
            user_id = match.group("user_id")
            user_name = await self._get_group_member_name(
                websocket,
                group_id=group_id,
                user_id=user_id,
            )
            if not user_name:
                continue
            hydrated_content = hydrated_content.replace(
                f"@用户({user_id})",
                f"@{user_name}({user_id})",
            )

        if hydrated_content == message.content:
            return message
        return IncomingMessage(
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            user_name=message.user_name,
            content=hydrated_content,
            is_group=message.is_group,
            mentioned_bot=message.mentioned_bot,
            reply_action=message.reply_action,
            reply_params=message.reply_params,
        )

    async def _get_group_member_name(
        self,
        websocket: Any,
        *,
        group_id: str,
        user_id: str,
    ) -> str | None:
        cache_key = (group_id, user_id)
        if cache_key in self._member_name_cache:
            return self._member_name_cache[cache_key]

        try:
            response = await self._onebot.call_action(
                websocket,
                "get_group_member_info",
                {
                    "group_id": group_id,
                    "user_id": user_id,
                    "no_cache": False,
                },
            )
        except TimeoutError:
            self._logger.warning(
                "get_group_member_info timeout: group=%s user=%s",
                group_id,
                user_id,
            )
            return None

        if response.get("status") != "ok":
            self._logger.warning(
                "get_group_member_info failed: group=%s user=%s response=%s",
                group_id,
                user_id,
                response,
            )
            return None

        data = response.get("data")
        if not isinstance(data, dict):
            return None
        user_name = self._read_member_name(data)
        if user_name is None:
            return None
        self._member_name_cache[cache_key] = user_name
        return user_name

    def _read_member_name(self, data: dict[str, Any]) -> str | None:
        for key in ("card", "nickname"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
