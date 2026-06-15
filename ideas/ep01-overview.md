# ep01 总览 / 选型复盘 — 素材稿（从 ep02 外迁）

> 这些内容原在 `ep02-video-render` 的 `tutorial.final.md` 里，按分期调整迁到 EP01 总览（含技术选型复盘）。属脑暴/素材，未定稿；EP01 最后制作时以此为底再加工。

---

## 一、判断层矩阵：Video-as-Code 的多条技术路线

> 护城河原则（见 `dev-log.md` 对「判断层」的重定义）：**判断层 = 边界 / 避坑指南**，不是中立百科式综述。每个方案必须回答「什么前提下成立 / 哪步会翻车」。

简单说，Video-as-Code 就是"用代码或数据把画面描述出来，再让程序编译成帧、合成视频"。实现这件事的工具不止一种——它们内核一致，差别只在用什么语言描述、用什么引擎渲染：

| 路线 | 代表项目 | 描述方式 | 典型场景 |
| :--- | :--- | :--- | :--- |
| **DOM / React 渲染** | Remotion | React 组件 + CSS/SVG，无头 Chrome 截图 | 前端栈、复杂排版、模板复用 |
| **TS 声明式动画** | Motion Canvas / Revideo | 生成器函数描述动画时序 | 代码演示、技术讲解动画 |
| **程序化数学动画** | Manim | Python 描述几何/公式动画 | 数学/算法可视化 |
| **像素 / 合成脚本** | MoviePy | NumPy 像素矩阵 + FFmpeg | 纯 Python、简单拼接 |
| **Canvas / 游戏引擎** | PixiJS / Cocos2d-HTML5 | Canvas 上下文逐帧绘制 | 复杂粒子、游戏化动画 |
| **命令式合成** | FFmpeg + 脚本 | filtergraph / 命令拼接 | 批量转码、轻量字幕烧录 |

判断层对比（每个方案的适用 / 不适用 / 已知坑）：

| 方案 | 语言/栈 | 核心机制 | 适用场景 | 不适用场景 | 已知坑 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Remotion** | React/TS | Node 端打包并求值 Composition，无头 Chrome 逐帧截图，FFmpeg 合成 | 前端栈、复杂 CSS/SVG、类型安全的跨期模板复用 | 零前端基础、纯后台超长批处理 | 模块顶层读 `window/document` 会在 Node 求值阶段崩溃；BUSL 商业授权 |
| **Motion Canvas / Revideo** | TS | 生成器函数声明动画时序，Canvas 渲染 | 代码演示、需精确时序编排 | 复杂网页级 Flex/Grid 排版生态不如 React | 组件/排版生态较小，复用模板需自建 |
| **Manim** | Python | 程序化描述几何/公式，逐帧渲染 | 数学/算法/公式可视化 | 一般 UI、网页排版、录屏混排 | 学习曲线陡，排版能力弱，渲染慢 |
| **MoviePy** | Python | NumPy 像素矩阵 + Imageio/FFmpeg | 纯 Python、简单拼接/裁剪、音轨闪避 | 自适应弹性排版、复杂文字动效 | 文本布局繁琐、多层画布内存大、无热更新 |
| **PixiJS / Cocos2d-HTML5** | JS | Canvas 上下文逐帧绘制 | 游戏类复杂粒子动画 | 标准网页 UI、文本对齐 | 文本换行与 DOM 对齐计算复杂 |
| **FFmpeg + 脚本** | Shell/任意 | filtergraph / 命令拼接 | 批量转码、轻量字幕烧录、合成兜底 | 复杂动效、交互式排版 | filtergraph 语法晦涩、调试困难 |

**怎么对号入座**：做"一期一个模板、字幕/代码卡片高复用"的硬核技术视频，看第 1 行（Remotion）；把录好的屏幕片段拼起来加 BGM 闪避，看第 4 行（MoviePy）；纯算法/数学缓动炫技，看第 2 行（Motion Canvas）。本项目主线落在 **Remotion（A 轨成片）+ MoviePy/FFmpeg（B 轨拼接闪避）** 的组合上。

**对比结论**：以"前端栈复杂排版 + 类型安全跨期复用 + AI 友好"为筛选条件，**Remotion** 是当前最优解；Motion Canvas/Revideo 是最接近的备选（更偏时序动画），其余按场景兜底。

---

## 二、技术路线选型理由（为什么选 Remotion）

选型不是"哪个最火选哪个"，而是回到本频道的核心约束：**固定模板 + 内容批量替换，让 AI 端到端接管，且跨期可维护**（见 `_decisions/why-remotion-over-hyperframes.md`，2026-06-01 已确认推进 Remotion A 轨）。在这个约束下，Remotion 胜出有四个硬理由：

1. **数据驱动模板，类型安全跨期复用（决定性）**：Remotion 的 `data.ts → Episode.tsx → template/` 四层结构（theme/primitives/scenes/episodes）天生适合"模板与数据分离"。TypeScript 保证每期换数据时格式不出错，改一处主题样式全期生效。
2. **AI Agent 友好**：每期不让 AI 自由发挥结构，只让它"填数据 + 微调 CSS"——这是 AI 最稳的活，幻觉空间最小。
3. **CLI 原生、易自动化**：`npx remotion render` 是纯命令行，可 `subprocess`、可上云，为后续"IDE 交互 → 后台 API 自动化"留好了口子。
4. **网页生态红利**：完整 CSS/SVG/Flexbox/动效库随手可用，信息密度和排版自由度远高于像素/Canvas 方案。

| 维度 | ✅ Remotion（数据驱动模板） | ❌ HyperFrames（HTML 复制粘贴） | 结论 |
| :--- | :--- | :--- | :--- |
| 模板复用/类型安全 | TS 约束、跨期安全 | HTML 无类型检查 | ✅ Remotion |
| AI 友好度 | 结构稳定、AI 只填数据 | 直接写 HTML，结构易漂移 | ✅ Remotion |
| 长期维护 | 改一处全期生效 | 10 期后维护困难 | ✅ Remotion |
| 授权 | BUSL（规模化付费） | Apache 2.0 | ⚠️ HyperFrames 更宽松 |

**选型代价（如实交代）**：Remotion 基于 React 技术栈，并采用 BUSL 商业授权（规模化商用需付费）。前端基础这块不用担心——本项目正是让 AI 来写组件、填数据，人主要把控架构与内容取舍。此外有一个 SSR 类环境的常规约束（生成阶段容易踩），用一条规则就能让 AI 自动规避。

> EP01 总览时再补：为什么坚决不做数字人对口型 / AI 绘界面（反噱头护城河），与上面的选型代价合并讲。
