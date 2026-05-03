class Persona:
    def __init__(self, prompt: str):
        self._prompt = prompt

    def build_system_prompt(self, *, bot_name: str, is_group: bool) -> str:
        persona = self._prompt.format(bot_name=bot_name)
        prompt = (
            f"你的名字是「{bot_name}」，你当前的人设如下：{persona}"
            "如果历史消息里你以前的回复风格、人设或态度与当前人设冲突，"
            "只把那些历史回复当作事实上下文，不要模仿旧风格。"
        )
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
