# `market-research` 修改记录

## 来源与许可证

- 原始 Skill：`market-research`，作者/版权方：Affaan Mustafa（依据原仓库根目录 MIT 许可证）。
- 原始来源：[affaan-m/ECC/.agents/skills/market-research](https://github.com/affaan-m/ECC/tree/90606c8315ee09cafc303515c5f33024db6b9882/.agents/skills/market-research)。
- 对比基线：提交 `90606c8315ee09cafc303515c5f33024db6b9882`，核对日期：2026-10-23。该提交用于本次可复核对照；无法确认更早获取副本时实际使用的提交。
- 许可证：MIT。原仓库根目录的 `LICENSE` 已随适配包保留，版权声明及许可正文未改。
- Agnes 适配副本：名称 `market-research`；Codex 安装路径：`~/.codex/skills/market-research`。适配源工作副本位于 `.agents/skills/market-research`。

## 相对上游基线的文件差异

基线中的 Skill 目录包含 `SKILL.md` 和 `agents/openai.yaml`；四份 `references/` 文件及 `MODIFICATIONS.md` 为当前适配包新增文件。

- `SKILL.md`：改写 Skill 描述、触发条件与研究标准；新增研究模块路由、Quick Scan/Decision Memo/Deep Dive 深度选择、核心工作流、证据覆盖与建议门槛、工具/账户/研究边界、报告结构、可读性规则及质量门槛。2026-10-22 增加外部研究分流、证据规划、关键主张核验、单位换算记录及质量门槛失败处理；2026-10-23 增加 Quick Scan/Decision Memo 报告字段和来源注记，合并默认 Decision Memo 规则以消除重复。
- `agents/openai.yaml`：改写短描述和默认提示；展示名称及隐式调用设置保留。Codex 安装副本的默认提示使用 `$market-research`。
- `references/market-sizing.md`：新增市场定义、TAM/SAM/SOM 边界、估算方法、单位及算术核验指引。
- `references/competitor-analysis.md`：新增竞品/替代方案识别、统一比较维度及证据记录指引。
- `references/customer-demand.md`：新增客户细分、需求信号、样本限制，以及用户材料、公开信号和实际一手研究的区分指引。
- `references/trends-and-opportunity.md`：新增行业结构、趋势、政策、市场进入和机会分析指引。
- `LICENSE`：复制原仓库根目录 MIT 许可证全文，保留原版权声明。
- `MODIFICATIONS.md`：新增来源、基线、许可证、逐文件差异、适配边界及核验状态记录。

## 依赖、适配边界与核验状态

- 未新增脚本、代码依赖、MCP、付费数据服务或第三方 API Key 配置。
- Skill 中列举的工具名称不表示 Agnes 已集成这些工具；每次运行需检查当前会话实际可用能力。Agnes 桌面端/Web 端能力覆盖、导入后的文件保留情况及 Agnes 运行兼容性未验证。
- 已对照上游基线的 `SKILL.md`、`agents/openai.yaml`，并确认四份研究参考文件及本记录未出现在该基线 Skill 目录中。
- 已核对包内 `LICENSE` 与基线仓库根目录 `LICENSE` 内容一致。
- 已核对本文件所列文件均存在；静态文件/内容核验不代表 Agnes 导入或调用测试通过。
