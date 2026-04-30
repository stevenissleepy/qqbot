# 最简单的 QQ 机器人

有人在频道或群聊里 @ 机器人时，机器人回复：

```text
hello
```

## Usage

在 .env 文件中加入

```sh
pip install -r requirements.txt
python main.py
```

## 运行

```powershell
python main.py
```

代码同时监听：

- `on_at_message_create`：频道里 @ 机器人
- `on_group_at_message_create`：群聊里 @ 机器人

如果你的机器人还没有群聊权限，只测试频道 @ 即可。
