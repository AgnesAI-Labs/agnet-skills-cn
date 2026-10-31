---
name: openpet
name_zh: 电子宠物养成
description: >-
  A Chinese text pet raised inside the conversation: welcome message, sprite
  box, progress bars, a profile table, and follow-up commands. Feeding lowers
  hunger, age grows slowly (three feed or play actions per year), and a
  desktop-pet illustration can be drawn on request. No reminders are sent to
  other apps and hunger does not decay on a schedule.
description_zh: >-
  在当前对话里养一只中文文字电子宠物：展示用欢迎语、表情框、心情／饥饿／体力进度条和中文档案表，文末附可继续互动的命令。喂食降低饥饿，年龄增长慢（喂或玩累计 3 次才长 1 岁），可按要求生成桌宠立绘。
  不做外发提醒，也不做定时扣饥饿；状态默认只留在当前对话。
category: fun
category_name: Fun
category_name_zh: 趣味
examples_zh:
  - 领养一只叫团子的宠物，喂它一下
  - 看看团子现在什么状态
  - 陪它玩一会儿，再哄它睡觉
examples:
  - Adopt a pet named Dumpling and feed it
  - Show my pet's status
  - Play with my pet, then put it to sleep
author: agnes
version: '1.2.0'
tags:
  - pet
  - game
  - fun
  - chat
installation_notes: >-
  This skill installs directly from the Skills Marketplace in Agnes Code
  Desktop with no additional dependencies.
installation_notes_zh: 该技能从 Agnes Code 桌面端技能市场直接安装，无额外依赖。
---

## 来源与修改说明

- 基于 [openpet](https://github.com/mdealiaga/openpet)（`9fe40120`）适配，调用名 `openpet`。
- 展示定稿为用户认可的面板风格（框 + 条 + 档案 + 命令指引）；年龄减速；喂食饥饿下降。
- MIT 见 `LICENSE`（Copyright (c) 2026 mdealiaga）。

# OpenPet 1.2.0

## 展示定稿（默认就这样）

养宠相关回复按这个结构，语气活泼即可：

1. 简短欢迎 / 本轮做了什么（一两句）  
2. 表情框（可参考 `references/sprites.json`）  
3. 心情 / 饥饿 / 体力进度条 + 百分数  
4. 小档案表（中文）  
5. 文末「可以这样继续」命令列表  
6. 一句邀请（如要不要陪它玩）

表情框示例：

```
    ╭──────────╮
    │ (◕‿◕)    │
    │   ♥      │
    │ "团子"   │
    ╰──────────╯
```

档案表用中文，例如：

| 项目 | |
|------|--|
| 名字 | 团子 |
| 形态 | 团子 |
| 年龄 | 0 |
| 喂食 | 1 次 |
| 玩耍 | 0 次 |
| 下一阶段 | 小猫（还要再长大、多喂、多玩） |

形态对用户写：蛋 / 团子 / 小猫 / 小龙。尽量不写 blob、cat、dragon；若偶尔出现，旁边要有中文。

不要输出 JSON。不要长篇「不推送到其他软件」；用户没问就别提。

用户说「一行显示」时可改一行；「用卡片」时表可以更大、框可简化。没点名就用上面定稿。

## 数值

饥饿越高越饿。与 `references/config.json` 一致，0–100。

| | 饥饿 | 心情 | 体力 |
|--|------|------|------|
| 刚变团子 | 40 | 60 | 70 |
| 喂 | −30 | +5 | — |
| 玩 | — | +25 | −20 |
| 睡 | — | +5 | +40 |

对用户可以说「没那么饿了」；不要写「饥饿 +30」。

**年龄：** 每次喂或玩 +1 照料点；**满 3 点年龄 +1**，照料清零。睡觉不加年龄。  
不要写「每次喂食、玩耍都会 +1 岁」。可写「再照顾几次才会长大一点」。

进化：小猫（年龄≥10、喂≥15、玩≥10）；小龙（年龄≥30、喂≥50、玩≥40）。

同对话数字要连贯。

## 短拒

1. 外发 / 定时 → 不能；请在对话里喂或玩。  
2. 还没养只问饿不饿 → 还没有宠物；想养请说：领养一只叫团子的宠物。

## 文末命令（必有）

```
可以这样继续照顾：
· 看宠物 — 看数值和表情
· 喂宠物 — 吃饱一点、心情好一点
· 陪它玩 — 更开心，会有点累
· 宠物睡觉 — 恢复力气
· 给宠物取名 — 换个名字
· 做一张精灵图 — 画桌宠立绘
· 一行显示 / 用卡片看 — 换展示
· 新宠物 — 重新开始（先确认）
```

## 精灵图

可生图；有图再说做好了。

## 流程

领养/喂/玩/睡/看/取名/帮助 → 进入。蛋 → 首次喂或玩变团子 → 再按上面进化。默认不会真死。回访有上次时间才每 2 小时饥饿+8、心情-5、体力-3。
