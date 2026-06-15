# ep05 工作流构建 / ep06 角色编排 — 素材稿（从 ep02 外迁）

> 这些内容原在 `ep02-video-render` 的 `tutorial.final.md` §四里，按分期调整迁到 EP05（工作流构建）与 EP06（角色编排）。属脑暴/素材，未定稿。
> 注意：下方"七阶段流水线"与 `.windsurf/workflows/` 是旧叙事，**当前真相是 13 阶段 + `.devin/workflows/`**（见 `content-library/PIPELINE.md`）；EP05/EP06 制作时按真实状态机重写。

---

## 流程即代码：角色定义与工作流（Dogfooding）

既然视频的画面可以用代码控制，那么**制作这条视频的"内容工作流"本身，能不能也做成代码（Process-as-Code）？** 本项目的答案是肯定的——这才是频道真正的护城河（以行证言）。

### 1. 三件套：角色 = 视角，工作流 = 步骤，文件 = 状态机

| 资产 | 在仓库中的位置 | 在"流程即代码"里的角色 | 类比 |
| :--- | :--- | :--- | :--- |
| **角色（Roles）** | `shared/roles/` | 思考视角与边界（身份/能力/输出格式/不做什么） | LLM 的 `system_prompt` |
| **工作流（Workflows）** | `.devin/workflows/01→13` | 每个阶段的标准步骤与交互协议 | LLM 的 `user_prompt` 模板 |
| **状态（State）** | 产物 frontmatter `stage`/`status` + `PIPELINE.md` | 文件即数据的状态机，唯一进度真相源 | 编排器（Orchestrator） |

### 2. 流水线（角色 × 工作流映射）

> 旧素材为 7 阶段，现已是 13 阶段（01 选题 → 13 归档）。重写时以 `.devin/workflows/` 与 `PIPELINE.md` 为准。

| 阶段 | 工作流 | 主责角色 | 产物 |
| :--- | :--- | :--- | :--- |
| 01 选题分析 | `/01-topic-research` | 选题分析师 | 选题判断、标题候选、受众分析 |
| 02 内容策划 | `/02-content-planning` | 内容策划师 | 教学软文 + 分镜大纲 + 校验 JSON |
| 03 B站视听策划 | `/03-video-planning-bilibili` | 视觉策划师 | 组件映射、Props、动画 Cue、Zoom 指令 |
| 04 脚本撰写 | `/04-script-draft` | 文案撰稿人 | 分轨台词脚本 + 多平台改写 |
| 05 视频组装 | `/05-video-assembly` | 视频工程师 | Remotion 可渲染成片 |
| … | … | … | …（06 TTS → 13 归档见 PIPELINE.md） |

每个阶段都遵守同一套纪律：**读取角色文件 → 按其输出格式工作 → 不越界 → 关键节点停下等人确认 → 落盘并改 frontmatter 状态**。

### 3. 为什么这套"流程即代码"能被 AI 接管 / API 化

把"角色 = system_prompt、工作流 = user_prompt、frontmatter = 状态机"摆出来，一个最小编排器就能驱动整条线（伪代码）：

```python
import frontmatter, glob

# 状态机：扫描所有产物的 frontmatter，找到待推进的阶段
for path in glob.glob("content-library/**/README.md", recursive=True):
    post = frontmatter.load(path)
    if post.get("status") == "approved":        # 状态机读到"已确认"
        stage = post["stage"]                    # 如 02-content-planning
        role = load_role(stage)                  # 角色 = system_prompt
        steps = load_workflow(stage)             # 工作流 = user_prompt 模板
        run_agent(system=role, user=steps)       # 喂给 LLM，自动推进下一阶段
```

- **真正的难点是多模态物理限制**：A 轨（概念动画）可全自动，B 轨（真实 IDE 录屏，TAD-01 强制真人录制、禁止 AIGC 伪界面）必须人上传——所以流程里要设计"挂起等待"机制。
- 证据状态：本套角色/工作流文件**真实存在于本仓库**（`verified`）；"一个 Python 编排器即可端到端跑通"为 `paper_spec`，需后续做最小调度脚本验证。

### 4. 提示词链（Prompt Chain）示例

```text
Prompt-1（数据驱动，复用现成组件）：
基于 remotion-composer 现有的 @ComparisonCard 组件，生成"对比卡片"的数据配置，
左卡=方案A、右卡=方案B。只产出数据，不要新建组件。

Prompt-2（用规则把环境坑一次性封死）：
为 Cursor 在 .cursor/rules/ 下编写一份 mdc 规则，约束我编写 Remotion 组件时
自动加上 window/document/navigator 的安全守卫。
```

> 拆分建议：EP05 主讲"状态机 + Schema 校验门 + 断点续跑"，EP06 主讲"角色 = Prompt + 多智能体编排（pipeline_defs YAML）+ 挂起等待"。提示词链作为 EP06 的落地示例。
