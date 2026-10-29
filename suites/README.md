# 专家套件源

`suites/` 存放专家套件的组合声明。技能正文仍然只在仓库根目录各自维护，套件用声明引用它们，构建时才把被引用的目录收进包内。这样仓库里只有一份技能内容，套件里不会出现和原目录不一致的副本。

一个套件一个目录，目录里放 `suite.json`：

```json
{
  "id": "design-to-code",
  "name": "Design to Code",
  "name_zh": "设计稿转代码",
  "description": "Turn Figma designs and product requirements into production-ready frontend interfaces.",
  "description_zh": "把 Figma 设计稿和产品需求做成可直接上线的前端界面。",
  "version": "1.0.0",
  "category": "design",
  "tags": ["frontend", "figma"],
  "skills": ["frontend-design", "diagram-design"],
  "connectors": ["figma"]
}
```

## 字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `id` | 是 | 套件标识。匹配 `^[a-z0-9][a-z0-9.-]*$`，长度 1 到 64。构建时原样写进 `plugin.json` 的 `name`，两处必须一致 |
| `name` | 是 | 英文显示名，写进 `displayName` |
| `name_zh` | 是 | 中文显示名，写进 `displayNameZh` |
| `description` | 是 | 英文描述 |
| `description_zh` | 是 | 中文描述 |
| `version` | 是 | 版本号，只能包含字母、数字和 `. + -`，会进产物文件名 |
| `category` | 是 | 分类，写进 `plugin.json` 的 `category` |
| `tags` | 是 | 非空字符串列表，不能为空数组 |
| `skills` | 是 | 仓库根目录下的技能目录名，至少一个。只写目录名，不能写路径 |
| `connectors` | 否 | `mcp/servers.json` 里的条目 id，缺省视为没有连接器 |

`skills` 与 `connectors` 都不允许重复。

## 连接器

连接器只写 id，command 和 url 从 `mcp/servers.json` 取，套件声明里不重复维护一份地址。构建时按该条目转成 `plugin.json` 的 `mcpServers`：

- 条目有 `url`：转成 `{"type": "streamable-http", "url": "<url>"}`
- 条目有 `command`：按空格切开，第一个词作 `command`，其余作 `args`。例如 `"npx -y @playwright/mcp@latest"` 变成 `command: "npx"`、`args: ["-y", "@playwright/mcp@latest"]`
- 条目里 `url` 和 `command` 同时存在：构建报错。脚本不替你猜用哪种传输方式
- 两者都没有：构建报错

远程地址必须能解析成 http 或 https 链接，且不能带 query、fragment 或凭据，后端预检会直接拒绝这类值。脚本在打包前就拦下来。

## 包结构

ZIP 根目录只有两项：

```
plugin.json
skills/<技能目录名>/SKILL.md 及其原有附属文件
```

`plugin.json` 由构建生成，字段为 `name`、`version`、`displayName`、`displayNameZh`、`description`、`descriptionZh`、`category`、`tags`，声明了连接器时再加 `mcpServers`。技能走默认的 `skills/` 路径，所以不写 `skills` 字段。包内不生成 `.expert-suite-entry/`，后端安装时自己生成路由技能。

## 打包限制

限制与后端预检一致，任何一项不满足都会报错，并指出套件 id、技能目录和具体文件：

| 项目 | 上限 |
| --- | --- |
| ZIP 大小 | 60 MiB |
| 解压后总大小 | 80 MiB |
| 单个文件 | 10 MiB |
| 条目数 | 2000 |
| 单条路径层级 | 16 |
| 符号链接 | 不允许 |

任一套件校验失败时，整次构建以非零退出码结束，并且不写出任何包，避免留下半成品。

## 新增套件的步骤

1. 确认要引用的技能目录已经在仓库根目录，并且有 `SKILL.md`。
2. 新建 `suites/<套件 id>/suite.json`，按上面的字段填写。目录名只作容器，套件身份以 `id` 为准。
3. 需要连接器时，先确认 `mcp/servers.json` 里已有该条目，再把 id 填进 `connectors`。
4. 依次运行：

```bash
node scripts/validate-skills.mjs
node scripts/skills-security-scan.mjs
node scripts/build-expert-suites.mjs
```

5. 看构建输出的自检报告：包路径、条目数、最大单文件、解压后大小、ZIP 大小、符号链接、sha256。产物在 `dist/expert-suites/<id>-<version>.zip`，该目录已被 `.gitignore` 忽略。

`validate-skills.mjs`、`skills-security-scan.mjs` 和 `validate-skills.yml` 的忽略列表都包含 `suites`，套件声明不会被当成技能目录去要求 `SKILL.md`。前两个脚本还忽略 `dist`，构建产物不会被当成技能扫描。

## 可重复构建

同一份输入必须产出相同的字节，方便对 sha256。为此构建脚本把条目按路径排序、把文件时间固定为 1980-01-01 00:00:00、权限位固定为 0644，并用固定压缩级别。改了技能内容或套件声明，sha256 才应该变。
