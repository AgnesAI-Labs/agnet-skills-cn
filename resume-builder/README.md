# 可编辑简历构建器

从旧简历或真实经历建立一份可编辑 HTML 母版，并为 Word、PDF 和后续岗位定制准备经过确认的简历正文。

## 使用场景

- “用我的旧简历做一份可编辑的基础简历。”
- “我没有简历，帮我逐步整理经历后生成一份。”
- “把我确认过的简历正文做成 HTML，并准备一份 Word 版。”

## 输出与限制

本包可在文件能力实际可用时创建可编辑 HTML。包内包含六套样式、示例、HTML→PDF/PNG 渲染、版面测量、ATS 校验和仅监听本机回环地址的 Canvas 编辑器；首次运行需要在包内 `runtime/` 安装 Node 依赖、Playwright Chromium 和 Python 依赖，且必须获得用户明确授权。Word 可交给上层 Markdown 转 Office；没有实际文件产物时，只交付可复制正文和版式说明。

## 来源与许可

基于 [Chasen-Liao/resume-skills](https://github.com/Chasen-Liao/resume-skills) 的 `resume-builder` 适配，锁定提交 `a706ae3ad5f603d17d1c587bfb7f0b5abc6f8970`。本适配包遵循上游 MIT License；完整文本见 [LICENSE](LICENSE)。
