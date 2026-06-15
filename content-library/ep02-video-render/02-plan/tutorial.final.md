---
stage: 02-content-planning
kind: human-final
status: approved
source_workflow: /02-content-planning
---

> 👤 **本文件 = 人工修订定稿线（tutorial.final.md）**。正文初稿由自动产物 `tutorial.md` 原样拷入，**请在此文件上完成人工修订**（措辞/深度/取舍），改定后把上方 `status` 置回 `approved`。
> 下游 04 脚本以本文件为「口播内容真相源」，并须逐条覆盖文末「必讲要点覆盖清单」。
> 🔁 **本期主线**：站在"教人用 Vibe Coding"的角度，讲两件事——① 怎么用 Vibe Coding 选定技术路线；② 怎么用 Vibe Coding 把 Remotion 渲染引擎搭出来。流程即代码 / 角色编排留给 EP05 / EP06（素材见 `ideas/ep05-ep06-process-roles.md`）。
> 对齐真相源：`CONTENTLIB.md`（TAD-01 混合架构）、`shared/docs/remotion-spec.md`、`OpenMontage/remotion-composer/SCENE_TYPES.md`、`_decisions/why-remotion-over-hyperframes.md`。技术结论标 `verified` / `paper_spec`，未本机验证一律 `paper_spec`。

# 不写代码，用 Vibe Coding 搭一套能自动出片的视频渲染引擎

## 《Vibe Coding 造一条自动化视频生产线》EP02 · 视频渲染

---

## 一、开场：我没有前后端基础，凭什么能让视频"改一行就自动出片"

先说结论，再讲怎么做到的。

做技术教程视频，最烦的是改。传统剪辑（Premiere、剪映那一套）是在时间轴上一帧一帧地拖：换个数据要回去重排，改个标题要重新对位，一期视频改三轮，人就废了。

我的做法不一样：**把视频写成一份配置文件，让程序自动渲染出片**。要改哪儿，改配置里的一行字，重新跑一下，新的视频就出来了——不用碰时间轴。

但我没有前后端基础，这套东西不是我手写的。我全程用的是 **Vibe Coding**：不自己写代码，而是用大白话把想法讲给 AI，让 AI 去写、去改、去调，我只负责说清楚要什么、以及判断它做得对不对。

这一期就拆给你看，我是怎么用 Vibe Coding 走完这两步的：

1. **第一步——选路线**：市面上"把视频写成代码"的工具有好几种，我怎么靠和 AI 对话，选定了 Remotion；
2. **第二步——搭引擎**：选定之后，又怎么靠 Vibe Coding 一步步把 Remotion 渲染引擎搭起来、让它能按配置出片。

你跟着这套打法走，没有编程基础也能复制。

---

## 二、第一步：用 Vibe Coding 选技术路线

没基础的人最容易卡在第一步：工具那么多，我怎么知道该用哪个？答案不是自己去啃文档，而是**把选择题丢给 AI，但自己保留拍板权**。具体分三小步。

### 1. 先让 AI 把"能把视频写成代码"的路都摆出来

我给 AI 的话大概是："我想把视频做成代码或配置，让程序自动渲染出片，有哪些现成的技术路线？各自用什么来描述画面？" AI 列出来大致是这几条（内核都一样：**用代码/数据描述画面 → 程序编译成帧 → 合成视频**，区别只在用什么语言写、用什么引擎渲）：

| 路线 | 代表工具 | 用什么描述画面 | 适合干什么 |
| :--- | :--- | :--- | :--- |
| 网页（React + CSS）渲染 | **Remotion** | React 组件 + CSS/SVG，用无头浏览器逐帧截图 | 前端栈、复杂排版、模板复用 |
| 代码声明动画 | Motion Canvas / Revideo | 写函数描述动画时序 | 代码演示、讲解类动画 |
| 数学公式动画 | Manim | Python 描述几何/公式 | 数学、算法可视化 |
| 像素脚本拼接 | MoviePy | Python 操作像素 + FFmpeg | 纯 Python、简单拼接 |
| 画布/游戏引擎 | PixiJS / Cocos | 在 Canvas 上逐帧画 | 复杂粒子、游戏化动画 |
| 命令行合成 | FFmpeg + 脚本 | 命令拼接 | 批量转码、轻量字幕烧录 |

### 2. 别只听 AI 报菜名——逼它说清楚"边界和坑"

AI 默认会给你一份四平八稳的"百科式"对比，每个都说好话。这没用。**真正能帮你做决定的，是每条路"什么时候不好使、会在哪一步翻车"。** 所以我会追问："每个方案分别在什么情况下不适用？有哪些已知的坑？" 这样才逼出有判断价值的表：

| 方案 | 适合 | 不适合 | 已知的坑 |
| :--- | :--- | :--- | :--- |
| **Remotion** | 前端栈、复杂排版、跨期复用模板 | 纯后台超长批处理 | 组件顶层直接读浏览器对象会在打包阶段崩；商业授权是 BUSL（规模化要付费） |
| Motion Canvas / Revideo | 代码演示、精确时序动画 | 复杂网页级排版 | 组件/排版生态小，模板要自己攒 |
| Manim | 数学/公式/算法可视化 | 普通 UI、网页排版 | 学习曲线陡、排版弱、渲染慢 |
| MoviePy | 纯 Python、简单拼接、音轨闪避 | 自适应排版、复杂文字动效 | 文字排版繁琐、多层画布吃内存、改了要重跑 |
| PixiJS / Cocos | 游戏类复杂粒子动画 | 标准网页 UI、文字对齐 | 文字换行/对齐计算复杂 |
| FFmpeg + 脚本 | 批量转码、字幕烧录、兜底合成 | 复杂动效、交互排版 | 命令语法晦涩、难调试 |

> 这一步是 Vibe Coding 里最关键的"人保留判断"：AI 负责把信息铺开，**你负责盯着"坑"那一列做减法**。

### 3. 把自己的约束讲清楚，让 AI 帮我对号入座

选型不是"哪个火选哪个"，而是回到我自己的需求。我把约束讲给 AI：**我要一期一个固定模板、换数据就能批量出几十期；我要让 AI 自己改内容、不容易出错；我要跨好多期都好维护。** 在这几条约束下，Remotion 明显胜出（决策记录见 `_decisions/why-remotion-over-hyperframes.md`，`verified`）：

1. **固定模板、换数据就能复用**：Remotion 用 React 组件 + 数据分离，改一处主题样式，全系列生效。
2. **让 AI 干活最稳**：每期不让 AI 自由发挥结构，只让它"填数据、套现成组件"——这是 AI 最不容易出错的活。
3. **一行命令就能出片**：`npx remotion render` 是纯命令行，方便以后接自动化、上云。
4. **网页生态现成可用**：CSS、动效、图表库随手拿来，排版自由度高。

我还让 AI 把它和"直接复制粘贴 HTML"那种土办法做了对照：

| 比什么 | ✅ Remotion | ❌ 复制粘贴 HTML |
| :--- | :--- | :--- |
| 模板复用 | 改一处全系列生效 | 每期复制改，越改越乱 |
| 让 AI 接手 | 结构稳，AI 只填数据 | 结构容易跑偏 |
| 长期维护 | 十期后还能管 | 十期后维护困难 |
| 授权 | BUSL（规模化要付费） | 更宽松 |

**代价也如实说**：Remotion 是 React 技术栈、商业授权 BUSL（规模化商用要给钱）。前端基础这块不用怕——本来就是让 AI 写、我来把方向，这正是 Vibe Coding 的用法。它还有个"打包时不能乱碰浏览器对象"的小坑，用一条规则就能让 AI 自动绕开（见第三节）。

> **这一步的 Vibe Coding 心法**：把"选择"拆成 AI 擅长的"铺信息 + 列边界"和人擅长的"对着自己的约束做减法"。你不需要懂每个工具的源码，你需要会问、会删。

---

## 三、第二步：用 Vibe Coding 搭 Remotion 渲染引擎

路线定了，接下来是把引擎搭出来。这一段你会看到：搭引擎其实也不靠手写代码，靠的是**和 AI 一起把"配置"和"组件"对上**。

### 1. 引擎怎么干活：一份配置，自动分发成画面

仓库里的渲染引擎是 `OpenMontage/remotion-composer/`（React + Remotion，`verified`）。它的干活方式很直白：**你写一份配置，说清楚"这一段是什么画面、上面叠什么"，主程序 `Explainer` 就按配置里的 `type` 字段，自动找到对应组件去渲染**（完整清单见 `SCENE_TYPES.md`）。

观众看到的每一类画面，背后都对应一个现成组件，由 `type` 点名：

| 配置 `type` → 组件 | 做什么 |
| :--- | :--- |
| `comparison` → `ComparisonCard` | 左右对比卡 |
| `terminal_scene` → `TerminalScene` | 合成终端动画：命令+输出逐行打出，**不用真去录屏** |
| `screenshot_scene` → `ScreenshotScene` | 丢一张截图，脚本化叠光标/点击/打字——15–30 秒的聚焦演示足以乱真 |
| `bar_chart`/`line_chart`/`pie_chart`/`kpi_grid` → `charts/` | 各种图表动效 |
| `ConceptScene` / `SplitLayout` | 概念图解 / 左右分屏 |
| `section_title`/`stat_reveal`/`provider_chip`（叠层） | 小节标题 / 角标 / 模型名轮播 |
| `CaptionOverlay` | 字幕高亮（接口已留，**卡点见 EP03**） |

> 一句话：做一期内容 ≈ **挑组件、填字段**，不是从零摆时间轴。

### 2. 配置即内容：让 AI 填字段，别让它造组件

这是用 Vibe Coding 做视频最省心的地方。我不让 AI 去发明新组件，只让它**照着现成组件填一份配置**。比如要一个对比卡，我说"做一个对比卡，左边传统剪辑、右边代码即视频"，AI 产出的就是这么一份配置：

```jsonc
// ✅ 只写配置：一个 comparison，Explainer 自动渲成对比卡
{
  "type": "comparison",
  "title": "传统剪辑 vs 代码即视频",
  "leftLabel": "传统剪辑",   "leftValue": "拖时间轴，改一处全手工重排",
  "rightLabel": "代码即视频", "rightValue": "改一行配置，重新编译出片"
}
// ❌ 反面：让 AI 为这一期从零手写一个新组件 ComparisonScene.tsx——
//    既重复造轮子，又把"换数据就复用"的好处弄没了。
```

为什么这么干最稳？因为 Remotion 用 TypeScript 给每个 `type` 的字段都定好了格式，**AI 填错、漏填，编译时立刻报错**。AI 只在一个格子固定的表格里填空，乱发挥的空间被压到最小——这正是为什么没有编程基础也能让它干得住。

### 3. 给视频配个 3D 主持人（基础版）：站得稳就行

渲染引擎里还有个数字主持人 `VRMAvatar`（`src/components/VRMAvatar.tsx`，`verified`）。先把定位说死：**它只是画面里的陪衬主持，不是主角。**

- **渲染一次、按场景取景**：主持人整体渲一次，再按不同场景裁出半身/全身等景别，不用每个场景重搭。
- **得站得稳**：之前待机动作只摆髋部，结果整条腿带着脚像钟摆一样甩。修法是**在大腿上把髋部的左右摆动反向抵消掉**，让脚踩在原地、上半身还能自然摆；再去掉会让脚横向滑的整体位移。（`verified`：本期已修，见 PR「plant VRM feet」。）
- **划清边界**：我们**坚决不做对口型数字人、不做 AI 生成的假界面**——技术可信度靠真实录屏，主持人只串场。口型、表情这些更重的能力，留到以后单独做一期再说（已记进 `ideas/backlog.md`），那一期的角度就是"为什么只做个站得稳的陪衬，而不做对口型数字人"。

### 4. 避坑 + 出片：把规则写死交给 AI，渲染只是一行命令

搭引擎时唯一反复踩的坑：**别在组件最外层直接读 `window` 这类浏览器对象**，否则 Remotion 在打包阶段（跑在 Node 里、还没进浏览器）就直接报错。

与其每次盯着 AI，不如把这条规则一次写死，让 AI 以后自动遵守：

```tsx
// ❌ 打包阶段就崩：ReferenceError: window is not defined
const w = window.innerWidth;

// ✅ 加个判断再读
const getWidth = () => (typeof window !== 'undefined' ? window.innerWidth : 1920);
```

把这条写进 `.cursor/rules/remotion-ssr.mdc`（指向 `remotion-composer/src/**`），之后 AI 生成组件就会自动带上这个判断，不用人盯。这也是 Vibe Coding 的一个要点：**重复的约束，用规则固化下来交给 AI，而不是每次口头提醒。**

到了出片这一步，人不用写代码也不用背命令，让 AI 在终端里跑就行：

```bash
cd OpenMontage/remotion-composer
npx remotion studio                                   # 可视化调试
npx remotion render src/index.ts <CompositionId> out/demo.mp4
```

（`paper_spec`：`<CompositionId>` 具体注册名录制前让 AI 跑一次 `studio` 核对。）

---

## 四、总结

- **整期就两步**：用 Vibe Coding 选路线（让 AI 铺信息+列坑，人对着约束拍板）→ 用 Vibe Coding 搭引擎（填配置、套组件、规则兜底、AI 跑渲染）。
- **为什么是 Remotion**：固定模板换数据就复用、让 AI 接手最稳、一行命令出片、网页生态现成；代价是 React 栈 + BUSL 授权，但对"让 AI 写、人把方向"的打法不构成门槛。
- **引擎的核心**：一份 `cut`/`overlay` 配置 → `Explainer` 按 `type` 分发到现成组件 → 编译出片；做内容 = 挑组件、填字段。
- **数字主持人只做陪衬**：站得稳、按场景取景，坚决不做对口型数字人。
- **没有编程基础也能复制**：你要会的是"把需求和约束讲清楚、看住坑、把重复规则固化给 AI"，而不是手写每一行代码。

下一期 **EP03「字幕匹配」**：用 Whisper 拿到精确到字的时间戳，自动驱动 `CaptionOverlay`，让字幕踩着话音跳。

---

## 必讲要点覆盖清单（Coverage Checklist）

> 用途：本期口播（04 脚本）必须逐条讲到下列要点。人工定稿可增删，但删除须确认确实不讲。04 自查时逐条勾选。
> ⚠️ 本清单已按"用 Vibe Coding 选路线 + 搭引擎"的新结构重写；下游 03 分镜（README）与 04 脚本需按本清单同步重做。

### 一、开场（结果先行 + Vibe Coding 人设）
- [ ] 痛点用大白话：传统剪辑改一处要回时间轴重排，很累
- [ ] 结果先行：把视频写成配置，改一行就重新自动出片
- [ ] 人设：没有前后端基础，全程用 Vibe Coding（讲需求、AI 写、人判断）
- [ ] 本期路线图：第一步选路线、第二步搭引擎，没基础也能复制

### 二、用 Vibe Coding 选技术路线
- [ ] 让 AI 摆出多条路线：Remotion / Motion Canvas·Revideo / Manim / MoviePy / PixiJS·Cocos / FFmpeg（内核都是"代码描述→编译成帧→合成"）
- [ ] 开源方案对比，关键是逼 AI 给"不适用 + 已知坑"，人盯着坑做减法
- [ ] 选型理由：回到自己的约束（固定模板批量复用 / 让 AI 接手 / 跨期维护）→ 为什么选 Remotion
- [ ] Remotion vs 复制粘贴 HTML 的对照；代价如实说（React 栈 + BUSL 授权）

### 三、用 Vibe Coding 搭 Remotion 渲染引擎
- [ ] 引擎怎么干活：一份配置 → `Explainer` 按 `type` 分发到组件
- [ ] 组件清单：`comparison/terminal_scene/screenshot_scene/charts/ConceptScene·SplitLayout`；合成终端/截图无需真录
- [ ] 配置即内容：让 AI 填字段、别造组件；TypeScript 字段类型兜底，AI 乱发挥空间最小
- [ ] 数字主持人（基础版）：陪衬定位、脚站稳（本期已修复）、坚决不做对口型
- [ ] 避坑：顶层读 `window` 会在打包阶段崩 → 用 `.cursor/rules` 一次写死交给 AI
- [ ] 出片就是一行 `npx remotion render`，交给 AI / 终端跑

### 四、结尾 CTA
- [ ] 两步法回顾 + "没编程基础也能复制"的落点
- [ ] 关注引导 + 下期预告（EP03 字幕匹配：Whisper 字级时间戳驱动 `CaptionOverlay`）
