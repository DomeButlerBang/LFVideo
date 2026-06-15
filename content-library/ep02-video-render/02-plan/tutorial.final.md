---
stage: 02-content-planning
kind: human-final
status: draft
source_workflow: /02-content-planning
---

> 👤 **本文件 = 人工修订定稿线（tutorial.final.md）**。正文初稿由自动产物 `tutorial.md` 原样拷入，**请在此文件上完成人工修订**（措辞/深度/取舍），改定后把上方 `status` 置回 `approved`。
> 下游 04 脚本以本文件为「口播内容真相源」，并须逐条覆盖文末「必讲要点覆盖清单」。
> 🔁 **本期已按分期调整收敛为"渲染引擎"单一主题**：选型对比/为什么 Remotion → EP01 总览（素材见 `ideas/ep01-overview.md`）；流程即代码/角色编排 → EP05/EP06（素材见 `ideas/ep05-ep06-process-roles.md`）。本文只保留指针，不展开。

# 代码即视频（Video-as-Code）：把一份配置编译成画面

## 《Vibe Coding 造一条自动化视频生产线》EP02 · 视频渲染

> 📌 **本文性质**：本期教学软文，作为整期视频的核心灵魂与信息唯一真相源。对齐三处真相源：`CONTENTLIB.md`（TAD-01 混合架构）、`shared/docs/remotion-spec.md`（组件清单与 §1.9 映射）、`OpenMontage/remotion-composer/SCENE_TYPES.md`（场景分发）。所有技术结论显式标注证据状态（`verified` / `paper_spec`）与验收标准，未经本机渲染验证的一律 `paper_spec`。

---

## 一、核心概念：代码即视频，帧即状态

传统剪辑（Premiere / FCPX / 剪映）的心智模型是**轨道 + 绝对时间轴**：在时间线上拖素材、对齐音频、手打字幕。对高频更新的技术教程、工具演示类视频来说，这是一场低 ROI 的体力活——每改一处都得回到时间轴上重新手工摆放。

**Video-as-Code（代码即视频）换了一套心智模型**：一条视频不再是"摆出来的画面堆叠"，而是一段**声明式的代码 / 数据**，由渲染器**编译**成帧序列再合成视频。它带来三个传统剪辑给不了的工程特性：

1. **可版本控制**：视频就是文本（代码 / JSON / YAML），能 diff、能 review、能 git 回滚。
2. **可参数化批量复用**：同一套模板换一份数据，就能批量产出几十期结构一致的视频——这正是本项目「固定模板 + 内容替换」的根。
3. **AI 友好**：让 AI 拖时间轴很难，让 AI 写代码 / 改数据 / 调 CSS 是它最擅长的事——视频生产因此第一次能被 AI 端到端接管。

> 一句话本质：**帧即状态（Frame as State）**——Video-as-Code 把"时间轴"变成了"代码/数据的函数"，给定一个时间点，渲染器算出该时刻画面长什么样。

> Video-as-Code 是一类范式，落地不止一条技术路线（Remotion / Motion Canvas / Manim / MoviePy / FFmpeg…），**为什么本项目选 Remotion、各路线边界对比，统一放到 EP01 总览讲**。本期只认一件事：**配置 → 编译 → 帧**，把这台编译器拆开给你看。

---

## 二、渲染引擎：remotion-composer 怎么把配置编译成画面

本期的主角是仓库里的渲染编译器 `OpenMontage/remotion-composer/`（React 19 + Remotion，`verified` 存在）。它的工作方式是**声明式分发**：你给一份描述"这一段是什么场景、叠什么元素"的配置，主合成 `Explainer` 按 `cut.type` / `overlay.type` 把它分发到对应的场景/叠层组件去渲染（见 `SCENE_TYPES.md`）。

### 1. 场景与组件系统（A 轨成片的积木）

组件都封装好了（`verified` 存在）：通用组件在 `src/components/`，成套场景/原语在 `src/custom-templates/`。观众看到的每一类画面，背后都对应一个组件，由配置里的 `type` 字段点名：

| 配置 `type` → 组件 | 在哪 | 做什么 |
| :--- | :--- | :--- |
| `comparison` → `ComparisonCard` | components/ | 左右对比卡 |
| `terminal_scene` → `TerminalScene` | components/ | **合成终端动画**：命令+输出逐行打出，无需真录 |
| `screenshot_scene` → `ScreenshotScene` | components/ | 丢一张截图，脚本化叠光标/点击/打字——15–30s 聚焦演示可以假乱真 |
| `bar_chart`/`line_chart`/`pie_chart`/`kpi_grid` → `charts/` | components/ | 图表动效 |
| `ConceptScene` / `SplitLayout` | custom-templates/ | 概念图解 / 左右分屏 |
| overlay：`section_title`/`stat_reveal`/`provider_chip` | components/ | 小节标题 / 角标 / 模型轮播 |
| `CaptionOverlay` | components/ | 字幕高亮（接口已留，**卡点见 EP03**） |

> 关键认知：做一期内容 ≈ **挑组件、填字段**，而不是从零摆时间轴。完整 `type` 清单见 `SCENE_TYPES.md`。

### 2. 配置即内容：填字段，不造组件

渲染引擎不靠"每期写新组件"，而靠**一份配置**：把视频拆成一串 `cut`（主画面）和 `overlay`（叠层），每个对象就一个 `type` + 几个字段，`Explainer` 按 `type` 找到组件渲染。做一期 ≈ 挑 `type`、填字段：

```jsonc
// ✅ 只写配置：一个 comparison cut，Explainer 自动渲成对比卡
{
  "type": "comparison",
  "title": "传统剪辑 vs 代码即视频",
  "leftLabel": "传统剪辑",   "leftValue": "拖时间轴，改一处全手工重排",
  "rightLabel": "代码即视频", "rightValue": "改一行配置，重新编译出片"
}
// ❌ 反面：为这期从零手写一个 ComparisonScene.tsx——
//    既重复造轮子，又破坏了"配置即内容、组件可复用"的模板复用性。
```

TypeScript 给每个 `type` 的字段做类型约束：填错、漏填，编译期就报错。这就是"跨期换数据不翻车"的底气——也是为什么这套流程交给 AI 最稳：它只填格式固定的字段，幻觉空间被压到最小。

---

## 三、数字主持人（基础版）

渲染引擎里还有一个角色：3D 数字主持人 `VRMAvatar`（`src/components/VRMAvatar.tsx`，`verified`）。它的定位很克制——**只做画面里的"陪衬主持"，不是主角**。

- **渲染一次，按场景取景**：主持人整体渲染一次，再用取景预设（framing presets）按不同场景裁剪出半身/全身等景别，避免每个场景重复搭建。
- **站姿要"踩得稳"**：待机动作只驱动髋部会让整条腿链（含双脚）像钟摆一样甩。做法是**在大腿上反向抵消髋部的 yaw/roll**，让脚踩在原地、保留上半身的重心偏移；并去掉会让脚横向滑动的整体位移。纯旋转、帧确定（frame-deterministic）。（`verified`：本期已修复，见 PR「plant VRM feet」。）
- **边界（判断层）**：本项目**坚决不做对口型数字人（`talking_head`/`lip_sync`）与 AIGC 伪界面**——技术可信度靠真实录屏，主持人只承担"陪衬/串场"。口型、表情、多机位等更重的能力留作 **"数字主持人"候选期**（见 `ideas/backlog.md`），成熟后单独成期，切入点是"为什么只做站得稳的陪衬主持人、不做数字人网红"。

---

## 四、核心实操与避坑

> 取向：人关心的是**工程结构与流程**，代码细节交给 AI——优先用现成组件传数据，环境约束用规则交给 AI 自动规避。

### 1. 避坑：把 SSR 环境约束用规则一次性封死

确需手写组件时，唯一要守的纪律是**别在模块顶层碰浏览器全局对象**：

```tsx
// ❌ Node 打包/求值阶段直接 ReferenceError: window is not defined
const w = window.innerWidth;

// ✅ 类型安全守卫
const getWidth = () => (typeof window !== 'undefined' ? window.innerWidth : 1920);

// ✅ 依赖 DOM 的库用挂载门控
const [mounted, setMounted] = useState(false);
useEffect(() => setMounted(true), []);
if (!mounted) return null;
```

把这条写进 `.cursor/rules/remotion-ssr.mdc`（`globs` 指向 `OpenMontage/remotion-composer/src/**`），Cursor / AI 之后生成组件就会自动带守卫，一次性把这个约束封死，不用人盯。

> 技术精度：Remotion 在 **Node 端打包并求值 Composition 列表**（取时长/尺寸、做任务拆分），逐帧绘制发生在**无头 Chrome**里。崩溃点是"模块/组件求值阶段在 Node 读了浏览器全局对象"，不是"逐帧 SSR"——这决定了你该往哪查 bug。

### 2. 渲染出片：一行命令交给 AI / 脚本代跑

到了"产出数据 → 套组件 → 渲染出片"这一步，人不必逐行写代码、也不必背命令：

```bash
cd OpenMontage/remotion-composer
npx remotion studio                                   # 可视化调试
npx remotion render src/index.ts <CompositionId> out/demo.mp4
```

- **让 AI 填数据、套现成组件**：人给出每段要展示什么，AI 按"只传数据"范式产出 `data`，复用 `@ComparisonCard / charts/` 等组件，不从零造轮子。
- **渲染命令交给 AI / CI 代跑**：出片就是一行命令，人只看产物。`<CompositionId>` 与具体注册名需录制前对齐，让 AI 跑一次 `studio` 核对即可（`paper_spec`：注册名待录制前核对）。

---

## 五、总结

- **Video-as-Code 是范式**：用代码/数据描述、编译成帧——本期把这台编译器（remotion-composer）拆开看。
- **渲染引擎 = 配置 → 分发 → 组件 → 帧**：`Explainer` 按 `cut.type`/`overlay.type` 分发到 `ComparisonCard / TerminalScene / charts / …` 等类型化组件。
- **配置即内容**：挑 `type`、填字段、复用现成组件，TypeScript 字段类型兜底；从零手写组件是反面。
- **数字主持人只做陪衬**：站得稳（脚不飘）、按场景取景；坚决不做对口型数字人（反噱头）。
- **据实标注**：未实测的命令/注册名一律标 `paper_spec`，录制前由 AI 跑一次核对。

下一期 **EP03「字幕匹配」**：向 Whisper 接口获取毫秒级字级时间戳 JSON，自动驱动 `@CaptionOverlay` 与卡点动效。

---

## 必讲要点覆盖清单（Coverage Checklist）

> 用途：本期口播（04 脚本）必须逐条讲到下列要点。人工定稿时可增删/调整，但删除要点须确认确实不讲。04 自查时逐条勾选。
> ⚠️ 本清单已随"渲染引擎单一主题"收敛重写；下游 03 分镜（README）与 04 脚本需按本清单同步重做。

### 一、核心概念 → 范式与痛点
- [ ] 传统剪辑 = 轨道+绝对时间轴，对高频更新技术视频是低 ROI 体力活
- [ ] Video-as-Code 三特性：可版本控制 / 可参数化批量复用 / AI 友好
- [ ] 一句话本质：**帧即状态（Frame as State）**——画面是"代码/数据的函数"
- [ ] "代码即视频 ≠ Remotion"：它是一类范式（**选型对比详见 EP01 总览**，本期不展开）

### 二、渲染引擎：场景/组件系统
- [ ] `Explainer` 按 `cut.type`/`overlay.type` 声明式分发场景/叠层
- [ ] 组件清单：`ComparisonCard / TerminalScene / ScreenshotScene / charts / ConceptScene·SplitLayout`；合成终端/截图无需真录
- [ ] 配置即内容：写 `cut`/`overlay` 配置（挑 `type`+填字段）、复用组件 ✅ vs 从零手写 ❌；TypeScript 字段类型兜底

### 三、数字主持人（基础版）
- [ ] `VRMAvatar` 定位 = 陪衬主持，渲染一次、按场景取景预设裁剪
- [ ] 站姿"脚不飘"：反向抵消髋部 yaw/roll 让脚踩稳（本期已修复，`verified`）
- [ ] 边界：坚决不做对口型数字人 / AIGC 伪界面；口型/表情留作候选期

### 四、核心实操与避坑
- [ ] SSR 守卫：顶层读 `window` ❌ vs `typeof window !== 'undefined'` 守卫 ✅（写进 `.cursor/rules` 交给 AI 自动带）
- [ ] 崩溃点是"Node 求值阶段读浏览器全局对象"，不是"逐帧 SSR"
- [ ] 渲染出片一行命令 `npx remotion render`，交给 AI / CI 代跑

### 五、结尾 CTA
- [ ] 渲染引擎 = 配置→编译→帧；数据驱动模板 + 现成组件
- [ ] 关注引导 + 下期预告（EP03 字幕匹配：Whisper 字级时间戳驱动 `@CaptionOverlay`）
