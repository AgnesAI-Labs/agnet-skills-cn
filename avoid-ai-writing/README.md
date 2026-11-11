# Avoid AI Writing

帮助审阅和改写英文 prose 中的常见 AI 写作模式。改写时保留原文事实、归属、语气和不确定性；检测模式只报告有目录依据的观察，不替用户改写。

本 Skill 的模式按英文校准，不能据此判断其他语言文本是否由 AI 撰写，也不能作为作者身份或 AI 来源证明。文件编辑仅适用于用户明确指定的 prose 文件；JSON、源码、配置等结构化文件会拒绝改写。

此版本强化“只输出最终稿”，并使长目录读取和引号脚本仅在任务需要时使用。

## 用法

调用 `$avoid-ai-writing` 并粘贴英文段落，例如：

> Rewrite this English paragraph to remove obvious AI-writing clichés. Keep all facts and attribution; return only the revised paragraph: [paste your paragraph]

来源：[Conor Bronsdon 的 avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)。本包保留 MIT 许可证。
