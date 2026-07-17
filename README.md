# astrbot_plugin_compatible_sealdice

让 AstrBot 与 SealDice 共处同一群聊时避免重复响应。

## 功能

- AstrBot 忽略以 `!`、`.`、`。`、`/` 开头的消息，不影响 SealDice 处理这些消息。
- 群聊收到 `.log on` 后，AstrBot 在该群停止响应所有消息。
- 群聊收到 `.log off` 后，AstrBot 在该群恢复正常响应。
- 静默状态按“消息平台 + 群号”分别保存，AstrBot 重载或重启后仍然有效。
- `.log on` 和 `.log off` 只控制群聊；私聊中的同名消息仅按前缀规则忽略。

插件不会回复确认消息，控制指令仍由 SealDice 正常处理。

## 要求

- AstrBot `>= 4.9.2`

## 安装

在 AstrBot WebUI 的插件管理页面中，通过仓库地址安装：

```text
https://github.com/DMHPJ/astrbot_plugin_compatible_sealdice
```
