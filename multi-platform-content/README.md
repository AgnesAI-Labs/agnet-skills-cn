# 多平台内容制作（Multi-Platform Content Creator）

一个面向公众的通用 Agent Skill：从一句想法、现有文章或资料出发，制作小红书、公众号、抖音、B站、知乎、视频号、微博以及 LinkedIn、Instagram、TikTok、YouTube 等平台的图文、短视频脚本与发布前素材。

**定位**：创作 + 内容重构 + 平台适配 + 素材整理。单篇单平台即可调用；多平台、批量及文件交付按需扩展。**不自动登录、管理账号或发布内容。**

## 适合谁

个人记录者、自媒体创作者、学生、知识传播者、商家、企业品牌/内容运营人员等。无需具备专业的运营或写作知识。

## 安装与调用

1. 下载 `multi-platform-content-flat.zip`。客户端支持直接导入 ZIP 时，选择该 ZIP；如客户端要求目录，解压到名为 `multi-platform-content/` 的文件夹，并确认 `SKILL.md`、`README.md`、`LICENSE` 位于该文件夹根目录。
2. 将 ZIP 或上述文件夹导入或安装到支持 Agent Skills 格式的客户端的 Skill 目录/市场。具体操作以客户端版本说明为准（Agnes 支持情况以实际安装结果为准）。
3. 用自然语言直接调用；客户端支持显式 Skill 选择时，可使用 `$multi-platform-content`。

示例：

- 「帮我写一篇小红书笔记：主题是新手养猫的第一次体检，语气轻松。」
- 「这篇公众号文章改成适合微博、知乎、LinkedIn 的版本，保留数据和引用。」
- 「我有一款收纳盒，卖点是可折叠。请做一个抖音30秒口播脚本，价格未知不要编。」
- 「把这份活动资料改成小红书、视频号和公众号的宣传内容，附发布前检查表。」
- 「只帮我把这段话的标题改得更吸引人，给五个选项。」

## 输出示例与交付层级

- **默认**：直接可复制的标题、正文、必要标签和 CTA（如果适用）。
- **多平台**：多个平台各自的版本，而不是同篇文案换名称。
- **完整素材包**：内容版本表、话题标签表、素材与规格检查表、发布前检查清单，以及按需的口播/分镜文稿。结构定义见 `references/batch-output-schema.md`。
- 实际文件、图片和视频是否可以生成取决于宿主 Agent 的文件/多媒体工具；不会声称未创建的文件已经存在。

## 文件说明

```text
multi-platform-content/
├── SKILL.md                     主技能指令（标准 YAML frontmatter）
├── README.md                    用户文档
├── LICENSE                      MIT 许可证
├── references/
│   ├── platform-guidelines.md   平台表达方式与动态规范核验
│   ├── content-formats.md       图文、文章、口播、分镜等格式
│   ├── adaptation-rules.md      内容改编与信息保真
│   ├── brand-voice.md           语气和品牌规范
│   ├── fact-rights-safety.md    事实、授权、隐私与风险
│   ├── quality-checklist.md     出稿质量检查
│   ├── visual-planning.md       画面、封面、生成提示词与素材状态
│   └── batch-output-schema.md  文件、字段及批量交付规范
├── templates/
│   ├── platform-content.md
│   ├── video-script.md
│   ├── carousel.md
│   ├── content-package.md
│   └── publishing-checklist.md
├── examples/
│   ├── idea-to-content.md
│   └── cross-platform-adaptation.md
└── tests/
    └── test-cases.md            触发、输出、边界测试用例
```

## 设计原则

1. **单篇可用**：从一句话直接产出完整内容。
2. **改编不失真**：保留原始事实，分平台改变表达方式。
3. **按需加载**：主指令控制工作流，详细规则按任务读取。
4. **无硬编码过期规格**：平台限制、素材尺寸和政策随时可能更新，实时需求需核验官方资料。
5. **文件按需生成**：不把 Excel 强制加在每个普通文案请求上。
6. **实物与规划分开**：素材生成和素材建议分别标识。

## 版本与授权

- Version: 1.0.6
- Author: **kiki 77** (GitHub: [debraday885-lab](https://github.com/debraday885-lab))
- License: MIT，详见 `LICENSE`
- 本技能没有必需的第三方依赖或网络调用脚本。

兼容性说明：按 [Agent Skills 公开规范](https://agentskills.io/specification) 的 `SKILL.md`、`references/` 结构组织；不同宿主客户端可能有自己的导入和运行限制。
