# 渲染环境与命令路径

视觉版的 PDF、截图和布局校验依赖完整运行时；只安装技能说明不代表渲染环境已经就绪。第一次渲染前，先定位并检查运行时，后续复用，不要每次重新安装。

## 路径约定

- 文档中的 `references/...` 相对于当前 `SKILL.md`；其他技能通过 `../resume-builder/...` 读取共享资料。
- 命令中的 `scripts/...` 和 `runtime/...` 都相对于本 Skill 根目录，不是用户私有简历目录。执行前把 Skill 根目录和 HTML、PDF、manifest 都解析为实际绝对路径。
- 完整运行时已随包置于 `runtime/`，包含 `package.json`、`lib/`、`bin/` 和 `requirements-test.txt`；渲染脚本位于 `scripts/`。真实简历始终留在 Skill 包外的私有目录。

## Windows 初始化

需要 Node.js ≥20、Python ≥3.10 和 Playwright Chromium。只有用户明确授权安装依赖后，才在 `<Skill 根目录>/runtime/` 执行以下命令；不要在用户项目目录安装：

```powershell
npm ci
python -m pip install -r requirements-test.txt
npx playwright install chromium
```

然后按实际路径运行：

```powershell
node "<Skill 根目录>/scripts/render_resume.mjs" --html "<私有目录>/resume_visual.html" --pdf "<私有目录>/resume_visual.pdf" --preview "<私有目录>/resume_visual.preview.png" --json
```

`node "<Skill 根目录>/runtime/bin/resume-skills.mjs" validate "<私有目录>/resume_visual.html" --check-layout --json` 默认先验收编辑字段；需要额外检查排版时添加 `--check-layout`。自动测量通过也不能替代 AI 实际打开整页截图。

## 不可验证时

缺少依赖、浏览器或可用的图像查看工具时，明确报告 PDF 渲染或视觉复核未完成，不生成“已验证”结论，不以旧 PDF、旧截图或旧 manifest 代替当前产物。可以继续保存事实和 HTML，待运行时可用后执行同一验证闭环。ATS-safe 的 HTML 静态审计使用 Python 验证脚本即可，不必为它启动 Canvas 或执行视觉密度检查。
