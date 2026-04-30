# QQBot

一个支持按会话切换 agent 的 QQ 机器人。默认支持：

- `builtin`：内置示例 agent，固定回复 `hello`
- `deepseekv4`：调用 DeepSeek API 进行单轮聊天

## 目录结构

```text
.
├── pyproject.toml
├── src/
│   └── qqbot/
│       ├── cli.py        # 命令行入口
│       ├── __main__.py   # python -m qqbot 入口
│       ├── agents/
│       │   ├── base.py       # Agent 协议和上下文
│       │   ├── builtin/      # 内置示例 agent
│       │   ├── deepseekv4/   # DeepSeek v4 agent
│       │   ├── factory.py    # 默认 Agent 注册
│       │   └── registry.py   # Agent 注册表
│       ├── bot/
│       │   ├── agent_manager.py # 当前会话 agent 状态
│       │   └── client.py        # botpy 事件适配
│       ├── commands/
│       │   ├── base.py       # Command 协议和上下文
│       │   ├── agent.py      # /agent 命令
│       │   ├── registry.py   # Command 注册表
│       │   └── router.py     # 命令解析和分发
│       └── config.py         # .env 配置读取
└── .env.example
```

## 配置

复制 `.env.example` 为 `.env`，并填写：

```sh
QQ_BOT_APPID=10*******
QQ_BOT_SECRET=oh******************************
QQ_BOT_AGENT=deepseekv4
DEEPSEEK_API_KEY=sk-********************************
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

`QQ_BOT_AGENT` 是启动后的默认 agent，可选值包括 `builtin` 和 `deepseekv4`。
`deepseekv4` 需要配置 `DEEPSEEK_API_KEY`。`DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL` 可以按需调整。

## 运行

```sh
pip install -e .
qqbot
```

也可以使用模块入口：

```sh
python -m qqbot
```

## QQ 聊天命令

在频道或群聊里 @ 机器人：

```text
/agent
/agent list
/agent use builtin
/agent deepseekv4
```

`/agent` 和 `/agent list` 会查看当前会话的 agent 与可用列表。
`/agent use <name>` 或 `/agent <name>` 会切换当前会话的 agent。

当前动态切换保存在内存中，重启后会回到 `.env` 里的 `QQ_BOT_AGENT`。

## 添加新命令

在 `src/qqbot/commands/` 下新增命令：

```python
from qqbot.commands.base import CommandContext


class PingCommand:
    name = "ping"
    description = "检查机器人是否在线"

    async def handle(self, args: list[str], context: CommandContext) -> str:
        return "pong"
```

然后在 `src/qqbot/cli.py` 里注册：

```python
command_registry.register(PingCommand())
```

## 接入新 agent

在 `src/qqbot/agents/` 下新增实现：

```python
from qqbot.agents.base import AgentContext


class MyAgent:
    name = "my_agent"
    description = "我的自定义 agent"

    async def reply(self, message: str, context: AgentContext) -> str:
        return "自定义回复"
```

然后在 `src/qqbot/agents/factory.py` 的 `build_default_registry()` 里注册：

```python
registry.register(MyAgent())
```
