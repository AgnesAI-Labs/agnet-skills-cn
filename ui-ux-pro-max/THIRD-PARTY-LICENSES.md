# 第三方许可与来源范围

核查日期：2026-10-23。此文件描述适配包实际携带的第三方目录元数据，不授予超出相关来源许可证的权利。

## 上游 Skill 仓库

- 来源：[`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/a38d04c3d5c298c851dbe5e6ee1965ee3de42cb5)，基线提交 `a38d04c3d5c298c851dbe5e6ee1965ee3de42cb5`。
- 仓库根 `LICENSE` 为 MIT，版权声明为 `Copyright (c) 2024 Next Level Builder`。完整文本随包保留在 `LICENSE`。
- 该根许可证声明只按上游仓库的实际适用范围记录；不据此推定第三方目录内容或后续生成的素材均由 MIT 覆盖。

## Google Fonts 目录元数据

- 随包文件：`data/google-fonts.csv`、`data/google-font-licenses.json`。许可快照 `data/google-font-licenses.json` 对应 Google Fonts 仓库 `METADATA.pb` revision `038b637da7b3fd956a4ed93ffc607c3d5e4ce172`，记录 1,934 个字体家族及逐字体许可类别。`data/catalog-summary.json` 记录的 8 个无法对应到仓库许可证元数据的候选字体没有进入可检索目录。
- Google Fonts [仓库 README](https://github.com/google/fonts/blob/main/README.md)明确说明：仓库顶层目录标示其中所有文件的许可类别；每个字体家族目录含有该家族的元数据 `METADATA.pb` 和对应许可证。README 也说明仓库中的字体在遵守各自许可条款的条件下允许再分发。因此，目录中的家族元数据按各自家族许可处理，而不是视为没有许可或统一适用 MIT。
- 许可类别统计：OFL 1,894 条、Apache 2.0 35 条、UFL 5 条。`google-font-licenses.json` 是许可类别索引，不是各家族完整许可证文本。本包只包含目录元数据，不含字体二进制文件；使用或分发具体字体文件时仍须查看该字体家族的完整许可及 Reserved Font Name 等适用条件。
- `data/data-provenance.json` 将 `google-fonts.csv` 的来源列为 Google Fonts Developer API 和 Google Fonts 仓库。Google [Developer API 文档](https://developers.google.com/fonts/docs/developer_api)说明 API 提供字体家族元数据；Google [API 服务条款第 5(e) 节](https://developers.google.com/terms)限制 API 返回内容的复制和分发，但明确保留内容权利人许可或适用法律允许的情形。Google Fonts 仓库的逐家族许可提供了相应元数据的许可依据；API 来源记录本身不构成“目录无许可”的证据。后续若加入字体家族目录许可范围之外的 Google 服务数据，应单独核查该数据的条款。
- 生成的项目若实际下载、嵌入或再分发某个字体，应遵守该家族的具体许可证；本目录快照不替代对字体文件的检查。

## Phosphor 图标目录元数据

- 随包文件：`data/phosphor-icons-upstream.json`，记录来源包 `@phosphor-icons/core` 2.1.1、1,512 个图标的名称、分类、标签、代码点和导入路径；不含图标 SVG 或图像文件。
- 来源仓库：[phosphor-icons/core](https://github.com/phosphor-icons/core)。`@phosphor-icons/core` 2.1.1 的 [npm 包页面](https://www.npmjs.com/package/@phosphor-icons/core/v/2.1.1)和上游 `package.json` 均声明 MIT；上游 [LICENSE](https://github.com/phosphor-icons/core/blob/main/LICENSE) 标注 `Copyright (c) 2023 Phosphor Icons`，完整 MIT 文本随包保存在 `licenses/PHOSPHOR-ICONS-LICENSE.txt`。随包仅有 1,512 条目录元数据，不含 SVG 图标或图像文件。

## 适用边界

此文件和随包许可证材料是来源及范围记录，不构成法律意见。未核实的许可范围不应描述为已获授权；后续生成物实际包含第三方字体、图标、图片或其他素材时，应对相应素材单独核对来源和许可。
