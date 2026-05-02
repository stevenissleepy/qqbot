# QQBot

一个基于 NapCat / OneBot v11 WebSocket 的 QQ 机器人，使用单一 `TurtleAgent`。

`TurtleAgent` 使用 OpenAI 兼容接口。群聊中它会持续阅读消息并维护上下文，但只有判断群友正在跟自己说话时才回复；私聊会直接回复。每个群和每个私聊都有独立上下文。

## 目录结构

```text
.
├── pyproject.toml
├── src/
│   └── qqbot/
│       ├── cli.py              # 命令行入口
│       ├── __main__.py         # python -m qqbot 入口
│       ├── agent/
│       │   └── turtle_agent.py # TurtleAgent
│       ├── bot/
│       │   └── client.py       # NapCat / OneBot v11 WebSocket 适配
│       ├── config.py           # .env 配置读取
│       └── utils/
│           └── logger.py       # 日志
└── .env.example
```

## 配置

复制 `.env.example` 为 `.env`，并填写：

```sh
NAPCAT_WS_URL=ws://127.0.0.1:3001
NAPCAT_ACCESS_TOKEN=

BOT_LOG_DIR=log
BOT_LOG_FILE=bot.log
BOT_LOG_LEVEL=INFO
MESSAGE_LOG_DIR=log
MESSAGE_LOG_FILE=message.log
MESSAGE_LOG_MAX_LENGTH=500

AGENT_DEFAULT_MODEL=sjtu
SJTU_BASE_URL=https://models.sjtu.edu.cn/api/v1
SJTU_API_KEY=sk-********************************
SJTU_MODEL=deepseek-reasoner
AGENT_NAME=龟龟
AGENT_CONTEXT_MESSAGES=20
```

`NAPCAT_WS_URL` 是 NapCat 的 OneBot v11 WebSocket 服务地址。
如果 NapCat 配置了 access token，把同一个值填到 `NAPCAT_ACCESS_TOKEN`。
`AGENT_DEFAULT_MODEL` 是启动后的默认模型。
可切换模型会从 `src/qqbot/agent/models/` 自动发现。每个模型 client 自己提供 `name` 并读取自己的环境变量；例如 `models/sjtu.py` 的 client 名字是 `sjtu`，并读取 `SJTU_BASE_URL`、`SJTU_API_KEY`、`SJTU_MODEL`。
`AGENT_NAME` 是 TurtleAgent 在群聊里识别“别人是否在跟自己说话”的名字。
`AGENT_CONTEXT_MESSAGES` 控制每个群/私聊保留的上下文消息数。

## 聊天命令

在私聊发送，或在群里 `@龟龟 /model sjtu`：

```text
/model list
/model sjtu
```

模型选择按群/私聊分别保存，重启后回到 `AGENT_DEFAULT_MODEL`。新增模型时，在 `src/qqbot/agent/models/` 下加一个模块，实现带 `name` 属性和 `chat()` 方法的 client，并提供 `build_model_client()`。

## 运行

```sh
conda activate qqbot
pip install -e .
qqbot
```

也可以直接使用 conda 环境里的解释器：

```sh
/home/qqbot/tools/miniconda3/envs/qqbot/bin/python -m qqbot
```
