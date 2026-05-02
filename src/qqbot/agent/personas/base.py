class Persona:
    def __init__(self, prompt: str):
        self._prompt = prompt

    def build_system_prompt(self, *, bot_name: str, is_group: bool) -> str:
        persona = self._prompt.format(bot_name=bot_name)
        prompt = f"你的名字是「{bot_name}」，你的人设如下：{persona}"
        if not is_group:
            return (
                "你是 QQ 私聊机器人。"
                f"{prompt}"
                "自然、简短地回复用户。"
            )

        return (
            "你是 QQ 群聊机器人。"
            f"{prompt}"
            "用户已经明确在跟你说话。"
            "群消息会以「[昵称(用户ID)] 内容」的形式出现。"
            "请用群聊口吻自然、简短地回复，不要输出 JSON。"
        )
