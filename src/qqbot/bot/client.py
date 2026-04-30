import botpy
from botpy import logging
from botpy.message import GroupMessage, Message

from qqbot.agents import AgentContext, AgentRegistry
from qqbot.bot.agent_manager import AgentManager
from qqbot.commands import CommandContext, CommandRouter


logger = logging.get_logger()


class QQBot(botpy.Client):
    def __init__(
        self,
        *,
        agent_registry: AgentRegistry,
        command_router: CommandRouter,
        default_agent: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._agent_registry = agent_registry
        self._command_router = command_router
        self._agent_manager = AgentManager(agent_registry, default_agent)

    async def on_ready(self):
        logger.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        reply = await self._build_reply(
            conversation_id=f"guild:{message.guild_id}:{message.channel_id}",
            user_id=message.author.id,
            content=message.content,
        )
        await message.reply(content=reply)

    async def on_group_at_message_create(self, message: GroupMessage):
        reply = await self._build_reply(
            conversation_id=f"group:{message.group_openid}",
            user_id=message.author.member_openid,
            content=message.content,
        )
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=reply,
        )

    async def _build_reply(self, *, conversation_id: str, user_id: str, content: str) -> str:
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
