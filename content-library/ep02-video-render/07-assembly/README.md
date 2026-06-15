---
stage: 07-video-assembly
status: draft
source_workflow: /07-video-assembly
upstream_inputs:
  - 04-script/README.md (status: draft)
  - 05-b-roll/README.md (status: suspended — A轨兜底)
  - 06-tts/assets/ (status: draft)
  - shared/docs/remotion-spec.md
---

# ep02 视频组装方案

> ⚠️ **重做版（对齐新 04 脚本 + 06 重合成）**：本组装方案逐条映射 04 契约块的 **13 段 `sections[]`**（id 1–13，禁止增删/合并/改写/重排），音轨为 06 重合成的 13 段 WAV（按 `manifest.json` 实测时长排时间轴）。旧的 16 场景（`帧即状态/七阶段流水线/三件套/编排器伪代码`，含 `@TimelineScene`）已删除，归 EP05/EP06。B 轨逐条来自 `05-b-roll`（本期 `suspended`，全部以 A 轨兜底）。

## 制作概要

| 维度 | 值 |
|------|---|
| **轨道** | A 轨为主（概念动画全自动），B 轨挂起（A 轨兜底） |
| **时长** | **363.90s（6 分 04 秒）** = 06-TTS 13 段实测时长累加（Piper 样片；切 CosyVoice 3 重合成后微调） |
| **分辨率** | 1920×1080 @ 30fps（B站 16:9 主版本） |
| **复用模板** | IntroScene / ConceptScene / TableScene / SplitLayout / TerminalScene / ScreenshotScene / ComparisonCard / OutroScene |
| **新增组件** | 无（全复用 remotion-spec.md §1.9 已有组件） |

---

## Remotion 结构（场景编排表）

| # | 04 段 | 音轨段 | 时间区间 | 场景 | 组件 | 轨道 / B 轨素材 |
|---|------|-------|---------|------|------|------|
| 1 | 1 | S01_open | 0:00–0:39 | 开场钩子 | `@IntroScene` | A |
| 2 | 2 | S02_routes_intro | 0:39–0:57 | 选路线①·共同内核 | `@ConceptScene` | A |
| 3 | 3 | S03_six_routes | 0:57–1:30 | 选路线①·六条路线 | `@ConceptScene` | A |
| 4 | 4 | S04_pitfalls | 1:30–2:20 | 选路线②·不适用+坑 | `@TableScene` | A（B轨 `b-ide-route-pitfalls` 兜底） |
| 5 | 5 | S05_why_remotion | 2:20–2:46 | 选路线②·为什么 Remotion | `@ConceptScene` | A |
| 6 | 6 | S06_vs_html | 2:46–3:11 | 选路线②·vs 复制粘贴 HTML | `@SplitLayout(@ComparisonCard)` | A |
| 7 | 7 | S07_dispatch | 3:11–3:38 | 搭引擎①·配置分发 | `@ConceptScene` | A |
| 8 | 8 | S08_config | 3:38–3:56 | 搭引擎①·配置即内容 | `@TerminalScene` | A |
| 9 | 9 | S09_fill_vs_build | 3:56–4:23 | 搭引擎①·造组件 vs 填数据 | `@SplitLayout` | A（B轨 `b-ide-config-fill` 兜底） |
| 10 | 10 | S10_avatar | 4:23–4:51 | 搭引擎②·数字主持人基础版 | `@ScreenshotScene` | A |
| 11 | 11 | S11_ssr | 4:51–5:25 | 搭引擎②·SSR 避坑 | `@SplitLayout` + `@TerminalScene` | A（B轨 `b-ide-ssr-crash`/`b-ide-ssr-fix` 兜底） |
| 12 | 12 | S12_render | 5:25–5:44 | 搭引擎②·一行出片 | `@TerminalScene` | A（B轨 `b-term-render` 兜底） |
| 13 | 13 | S13_cta | 5:44–6:04 | 结尾 CTA | `@OutroScene` | A |

> 上表 13 行与 04 脚本 `sections[]` 的 13 段（id 1–13）**一一对应**，不增删、不合并、不改写。时间区间 = 06-TTS 各段实测时长累加（见 `06-tts/manifest.json`），总计 363.90s。

---

## data.ts 结构设计

```typescript
// OpenMontage/remotion-composer/src/episodes/ep02-video-render/data.ts

import type { EpisodeData } from '../../template';

export const ep02Data: EpisodeData = {
  meta: {
    id: 'ep02-video-render',
    title: '不写代码，用 Vibe Coding 搭一套能自动出片的视频渲染引擎',
    subtitle: '《Vibe Coding 造一条自动化视频生产线》EP02 · 视频渲染',
    fps: 30,
    width: 1920,
    height: 1080,
  },
  audio: {
    // 06-TTS 13 段，startSec = 前序段实测时长累加（manifest.json）
    segments: [
      { id: 'S01_open',         file: './assets/S01_open.wav',         startSec: 0 },
      { id: 'S02_routes_intro', file: './assets/S02_routes_intro.wav', startSec: 39.28 },
      { id: 'S03_six_routes',   file: './assets/S03_six_routes.wav',   startSec: 57.12 },
      { id: 'S04_pitfalls',     file: './assets/S04_pitfalls.wav',     startSec: 89.87 },
      { id: 'S05_why_remotion', file: './assets/S05_why_remotion.wav', startSec: 140.23 },
      { id: 'S06_vs_html',      file: './assets/S06_vs_html.wav',      startSec: 166.12 },
      { id: 'S07_dispatch',     file: './assets/S07_dispatch.wav',     startSec: 191.06 },
      { id: 'S08_config',       file: './assets/S08_config.wav',       startSec: 217.61 },
      { id: 'S09_fill_vs_build',file: './assets/S09_fill_vs_build.wav',startSec: 236.19 },
      { id: 'S10_avatar',       file: './assets/S10_avatar.wav',       startSec: 262.70 },
      { id: 'S11_ssr',          file: './assets/S11_ssr.wav',          startSec: 290.60 },
      { id: 'S12_render',       file: './assets/S12_render.wav',       startSec: 324.84 },
      { id: 'S13_cta',          file: './assets/S13_cta.wav',          startSec: 343.83 },
    ],
  },
  scenes: [
    {
      id: 'S01', component: 'IntroScene', durationSec: 39.28,
      props: {
        title: '不写代码，用 Vibe Coding 搭一套能自动出片的视频渲染引擎',
        subtitle: '《Vibe Coding 造一条自动化视频生产线》EP02 · 视频渲染',
        roadmap: ['第一步：选技术路线', '第二步：搭渲染引擎'],
        background: 'particles',
      },
    },
    {
      id: 'S02', component: 'ConceptScene', durationSec: 17.84,
      props: {
        eyebrow: '第一步 · 选路线',
        heading: '先让 AI 把路都摆出来',
        items: [
          { label: 'INPUT', title: '用代码/数据描述画面' },
          { label: 'COMPILE', title: '程序编译成帧' },
          { label: 'OUTPUT', title: '合成视频' },
        ],
        animation: 'flow_arrows',
      },
    },
    {
      id: 'S03', component: 'ConceptScene', durationSec: 32.75,
      props: {
        heading: 'AI 摆出的六条路线',
        items: [
          { title: '网页渲染 · Remotion', desc: 'React 组件+CSS，无头浏览器逐帧截图' },
          { title: 'Motion Canvas/Revideo', desc: '写函数描述动画时序' },
          { title: 'Manim', desc: 'Python 描述几何/公式' },
          { title: 'MoviePy', desc: 'Python 操作像素+FFmpeg' },
          { title: 'PixiJS/Cocos', desc: 'Canvas 上逐帧画' },
          { title: 'FFmpeg+脚本', desc: '命令行合成' },
        ],
        footer: '同一内核：把画面编译成帧',
        animation: 'stagger_cards',
      },
    },
    {
      id: 'S04', component: 'TableScene', durationSec: 50.36,
      props: {
        eyebrow: "人盯着'坑'那列做减法",
        title: '六个方案的适合/不适合/已知坑',
        columns: ['方案', '适合', '不适合', '已知的坑'],
        rows: [
          ['Remotion', '前端栈、复杂排版、跨期复用', '纯后台超长批处理', '组件顶层读浏览器对象会在打包阶段崩；BUSL 授权'],
          ['Motion Canvas/Revideo', '代码演示、精确时序', '复杂网页排版', '生态小、模板要自攒'],
          ['Manim', '数学/公式/算法', '普通 UI、网页排版', '学习陡、排版弱、渲染慢'],
          ['MoviePy', '纯 Python、简单拼接', '自适应排版、复杂文字动效', '文字排版繁琐、多层吃内存'],
          ['PixiJS/Cocos', '游戏类粒子动画', '标准网页 UI、文字对齐', '换行/对齐计算复杂'],
          ['FFmpeg+脚本', '批量转码、兜底合成', '复杂动效、交互排版', '命令晦涩、难调试'],
        ],
        highlight_row: 0,
        highlight_column: 3,
      },
    },
    {
      id: 'S05', component: 'ConceptScene', durationSec: 25.89,
      props: {
        eyebrow: '回到我自己的约束',
        heading: '为什么是 Remotion',
        items: [
          { label: '模板', title: '固定模板换数据就复用', desc: '改一处主题全系列生效' },
          { label: 'AI', title: '让 AI 接手最稳', desc: '只填数据、套现成组件，最不容易出错' },
          { label: 'CLI', title: '一行命令就出片', desc: 'npx remotion render' },
          { label: 'WEB', title: '网页生态现成可用', desc: 'CSS/动效/图表库随手拿' },
        ],
        animation: 'number_highlight_sequence',
      },
    },
    {
      id: 'S06', component: 'SplitLayout', durationSec: 24.94,
      props: {
        left:  { component: 'ComparisonCard', title: '✅ Remotion', status: 'success',
                 points: ['模板复用：改一处全系列生效', '让 AI 接手：结构稳、只填数据', '长期维护：十期后还能管'] },
        right: { component: 'ComparisonCard', title: '❌ 复制粘贴 HTML', status: 'error',
                 points: ['每期复制改、越改越乱', '结构容易跑偏', '十期后维护是灾难'] },
        footer: '代价如实说：React 栈 + BUSL 授权（规模化商用要付费）',
      },
    },
    {
      id: 'S07', component: 'ConceptScene', durationSec: 26.55,
      props: {
        eyebrow: '第二步 · 搭引擎',
        heading: '一份配置 → Explainer 按 type 分发 → 现成组件',
        items: [
          { label: 'comparison', title: '→ ComparisonCard 对比卡' },
          { label: 'terminal_scene', title: '→ 合成终端：逐行打字，不用真录屏' },
          { label: 'screenshot_scene', title: '→ 截图叠光标/点击/打字' },
          { label: 'charts', title: '→ 柱/线/饼图、KPI' },
          { label: 'ConceptScene/SplitLayout', title: '→ 概念图解/左右分屏' },
        ],
        animation: 'dispatch_flow',
      },
    },
    {
      id: 'S08', component: 'TerminalScene', durationSec: 18.58,
      props: {
        title: '只写配置：一个 comparison',
        language: 'jsonc',
        code: `{
  "type": "comparison",
  "title": "传统剪辑 vs 代码即视频",
  "leftLabel": "传统剪辑",  "leftValue": "拖时间轴，改一处全手工重排",
  "rightLabel": "代码即视频", "rightValue": "改一行配置，重新编译出片"
}`,
        typing_speed: 'medium',
      },
    },
    {
      id: 'S09', component: 'SplitLayout', durationSec: 26.51,
      props: {
        left:  { component: 'TerminalScene', title: '❌ 从零手写组件', language: 'tsx',
                 code: `// 违反"换数据就复用"，还重复造轮子\nexport const ComparisonScene = () => {\n  return <div className="custom">...</div>;\n};` },
        right: { component: 'TerminalScene', title: '✅ 只填数据，复用现成组件', language: 'ts',
                 code: `const comparison = {\n  left:  { title: '传统剪辑',   value: '拖时间轴重排' },\n  right: { title: '代码即视频', value: '改一行配置重渲' },\n};\n// <ComparisonCard {...comparison} /> — TS 字段类型兜底` },
        fallback: 'TerminalScene',
      },
    },
    {
      id: 'S10', component: 'ScreenshotScene', durationSec: 27.90,
      props: {
        title: '数字主持人 VRMAvatar：只做陪衬串场',
        callouts: [
          { at: '取景', text: '整体渲一次，按场景裁半身/全身' },
          { at: '脚踩稳', text: '在大腿上把髋部摆动反向抵消，脚踩原地' },
          { at: '边界', text: '坚决不做对口型数字人、不做 AI 假界面' },
        ],
      },
    },
    {
      id: 'S11', component: 'SplitLayout', durationSec: 34.24,
      props: {
        left:  { component: 'TerminalScene', title: '❌ 打包阶段就崩', language: 'tsx',
                 code: `// Remotion 打包跑在 Node 里，没有 window\nconst w = window.innerWidth;  // 💥\n// ReferenceError: window is not defined` },
        right: { component: 'TerminalScene', title: '✅ 守卫 + 规则一次写死', language: 'tsx',
                 code: `const getWidth = () =>\n  typeof window !== 'undefined' ? window.innerWidth : 1920;\n\n// .cursor/rules/remotion-ssr.mdc（globs: remotion-composer/src/**）\n// "组件顶层不得直接读 window/document"` },
        fallback: 'TerminalScene',
      },
    },
    {
      id: 'S12', component: 'TerminalScene', durationSec: 18.99,
      props: {
        title: 'npx remotion render 出片',
        language: 'bash',
        code: `cd OpenMontage/remotion-composer\nnpx remotion studio                       # 可视化调试\nnpx remotion render src/index.ts \\\n  <CompositionId> out/ep02.mp4            # 渲染出片`,
        typing_speed: 'fast',
        show_progress: true,
      },
    },
    {
      id: 'S13', component: 'OutroScene', durationSec: 20.07,
      props: {
        headline: '整期就两步：用 Vibe Coding 选路线 + 搭引擎',
        summary: '讲清需求、看住坑、把规则固化给 AI — 没基础也能复制',
        next_episode: '下期 EP03 字幕匹配：Whisper 让字幕踩着话音跳',
        subscribe_text: '关注，别错过',
        background: 'gradient',
      },
    },
  ],
};
```

---

## Episode.tsx 骨架

```tsx
// OpenMontage/remotion-composer/src/episodes/ep02-video-render/Episode.tsx

import { Sequence, Audio, staticFile } from 'remotion';
import {
  IntroScene, OutroScene, ConceptScene, TableScene,
  TerminalScene, SplitLayout, ScreenshotScene, ComparisonCard,
} from '../../template';
import { ep02Data } from './data';

const FPS = 30;

export const Ep02Episode: React.FC = () => {
  const { scenes, audio } = ep02Data;
  let currentFrame = 0;

  return (
    <>
      {/* 音频轨 — 连续播放 13 段 TTS（startSec 来自 06 manifest） */}
      {audio.segments.map((seg) => (
        <Sequence key={seg.id} from={Math.round(seg.startSec * FPS)}>
          <Audio src={staticFile(seg.file)} />
        </Sequence>
      ))}

      {/* 画面轨 — 13 场景按编排顺序，duration = 对应 TTS 段时长 */}
      {scenes.map((scene) => {
        const from = currentFrame;
        const dur = Math.round(scene.durationSec * FPS);
        currentFrame += dur;
        return (
          <Sequence key={scene.id} from={from} durationInFrames={dur}>
            <SceneRouter component={scene.component} props={scene.props} />
          </Sequence>
        );
      })}
    </>
  );
};
```

---

## 渲染命令

```bash
# 开发预览
cd OpenMontage/remotion-composer && npx remotion studio

# 渲染 16:9 主版本
npx remotion render src/index.ts ep02-video-render out/ep02-video-render.mp4
```

---

## 需人工提供的素材（B 轨）

> 来源 = `05-b-roll/README.md`（阶段 `05-b-roll-recording`，当前 `suspended`，本期暂缓）。以下逐条对应 04 `b_track_assets_required`，本期均以 A 轨兜底；补录后把 05 改回 `approved` 即可替换：

| 素材 ID | 消费段（04 段 / 音轨段） | 描述 | A 轨兜底方案 |
|---------|------|------|------------|
| b-ide-route-pitfalls | 4 / S04_pitfalls | IDE 录屏：和 AI 对话追问每条路的"不适用+坑" | `@TableScene` 判断层矩阵（highlight 坑列） |
| b-ide-config-fill | 9 / S09_fill_vs_build | IDE 录屏：从零手写❌ vs 只填数据✅ | `@SplitLayout` 左右 `@TerminalScene` 代码对照 |
| b-ide-ssr-crash | 11 / S11_ssr | IDE 录屏：顶层读 window 触发 ReferenceError 红屏 | `@SplitLayout` 左 `@TerminalScene` 崩溃代码 |
| b-ide-ssr-fix | 11 / S11_ssr | IDE 录屏：typeof 守卫 + 写入 .cursor/rules mdc 一次通过 | `@SplitLayout` 右 `@TerminalScene` 守卫代码 |
| b-term-render | 12 / S12_render | 终端录屏：npx remotion render 出片（可选） | `@TerminalScene` render 命令 + 模拟进度 |

---

## 产出路径

```
OpenMontage/remotion-composer/src/episodes/ep02-video-render/
├── data.ts          # 文案与组件配置数据（13 场景 + 13 音轨段）
├── Episode.tsx      # 场景组装入口
└── assets/          # 13 段 TTS 音频（从 06-tts/assets/ 复制或 symlink）

OpenMontage/remotion-composer/out/
└── ep02-video-render.mp4  # 渲染成片（待 Remotion 工程接好新 data 后产出）
```

---

## 当前状态

- 组装方案已按新 04（13 段）+ 06 重合成（13 段 WAV、363.90s）对齐重写；旧 16 场景结构（含 `@TimelineScene` 七阶段）已弃用。
- **待办**：把上面的 `data.ts` 接进 `OpenMontage/remotion-composer` 工程、用 13 段新音频重渲 1080p 成片（旧成片基于已废弃的 16 段结构，需重渲）。
- 全部复用现有组件，无新组件工单；B 轨 5 条均有 A 轨兜底，B 轨补录前可先出 A 轨版。

```json
{
  "stage": "07-video-assembly",
  "episode": "ep02-video-render",
  "total_scenes": 13,
  "total_duration_seconds": 363.90,
  "audio_source": "06-tts/assets (piper-tts, 13 segments)",
  "track_breakdown": {
    "a_track_only": 9,
    "a_track_with_b_fallback": 4
  },
  "components_used": [
    "IntroScene", "ConceptScene", "TableScene", "SplitLayout",
    "ComparisonCard", "TerminalScene", "ScreenshotScene", "OutroScene"
  ],
  "new_components_required": 0,
  "remotion_project_status": "pending_rewire",
  "render_ready": false,
  "blocking_on": "把新 13 段 data.ts 接进 remotion-composer 并重渲"
}
```
