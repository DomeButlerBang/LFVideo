---
stage: 06-tts-synthesis
status: draft
source_workflow: /06-tts-synthesis
---

# ep02 TTS 语音合成规划

## 引擎推荐

| 维度 | 推荐方案 |
|------|---------|
| **首选引擎** | 豆包 TTS（`doubao_tts.py`） |
| **推荐理由** | 中文情感最自然；支持逐字时间戳（利于后续 08 字幕对齐）；长文本异步合成 |
| **备选引擎** | OpenAI TTS（中英混合段落较多时切换） |
| **离线备选** | Piper TTS（零成本本地引擎，紧急降级方案） |
| **输出格式** | WAV 44.1kHz / 16bit 单声道 |

### 引擎选择理由

本期 ep02 口播内容为 **纯中文技术讲解**（Remotion / React 视频渲染），虽含英文术语但主体为中文口语。豆包 TTS 在中文自然度和技术讲解场景的表现优于其他引擎：
- 停顿感和换气节奏接近真人
- 支持 `character-level timestamps`，直接输出逐字时间戳供 08 字幕阶段使用
- 长文本异步 API，单次可处理完整段落（无需按句切分）

---

## 口播段落拆分

从 `04-script/README.md` 提取的 5 段 `[口播]` 文本：

### 段落 1：开头黄金钩子（S1）

| 属性 | 值 |
|------|---|
| 场景 | S1 @IntroScene |
| 情感 | 钩子抓人 → 稍快、有力 |
| 预估时长 | 30s |
| 输出文件 | `voice-s01.wav` |
| 字数 | 约 150 字 |

**口播原文**：
> 你还在用 PR、AE 一帧一帧地剪视频吗？停。今天我要告诉你一个完全不同的思路。写代码，就是在写视频。一百行 React，直接编译成 4K 高清 MP4。这就是 Remotion。但别急着兴奋，这条路上有一个几乎所有 AI 都会踩的致命深坑。 SSR 渲染时，window is not defined。什么意思？就是你的代码在浏览器里跑得欢，一编译就崩。怎么解？一条 MDC 规则，被动约束，让 AI 自动写出安全代码。今天这期，手把手带你跑通。

**TTS 参数建议**：
- `speed`: 1.05（稍快于正常语速，制造紧迫感）
- 情感：激昂 + 好奇

---

### 段落 2：Remotion 底层解密（S2）

| 属性 | 值 |
|------|---|
| 场景 | S2 @TimelineScene |
| 情感 | 讲解型 → 稳重、清晰 |
| 预估时长 | 120s |
| 输出文件 | `voice-s02.wav` |
| 字数 | 约 200 字 |

**口播原文**：
> 先搞清楚 Remotion 的核心机制。视频的本质是什么？是帧。帧的本质是什么？是时间。Remotion 给你一个 `useCurrentFrame()` Hook，返回当前是第几帧。再给你一个 `useVideoConfig()`，返回 fps 和总帧数。简单除法，`frame / fps`，你就得到了当前时间点。这意味着什么？意味着你可以用 React 的状态、Props、Effect，来驱动视频的每一帧。想做一个进度条？监听 frame。想做动画插值？spring 物理公式直接上。你写的不是视频，是"时间的函数"。这才是代码即视频的真正含义。

**TTS 参数建议**：
- `speed`: 0.95（稍慢，留出思考空间）
- 在"视频的本质是什么？是帧。帧的本质是什么？是时间。"处插入 SSML `<break time="300ms"/>` 增强节奏感

---

### 段落 3：致命 SSR 踩坑（S3）

| 属性 | 值 |
|------|---|
| 场景 | S3 @ConceptScene + @VideoSlot |
| 情感 | 讲故事 → 先平叙，到报错处突然加重 |
| 预估时长 | 120s |
| 输出文件 | `voice-s03.wav` |
| 字数 | 约 220 字 |

**口播原文**：
> 好，原理明白了，开始实操。你让 Cursor 写一个 Remotion 组件，读取窗口宽度做响应式布局。代码看起来没问题，在浏览器预览里跑得欢。你信心满满，执行 `npx remotion render`，准备导出成片。啪，红屏。`ReferenceError: window is not defined`。为什么？Remotion 的渲染分两个阶段。第一阶段，SSR 预渲染，Puppeteer 在 Node.js 环境里截图。Node 里没有 window，没有 document，没有任何浏览器全局对象。你的代码在顶层直接读 `window.innerWidth`，Node 端直接崩溃。这不是你代码的问题，是 AI 的环境感知盲区。它不知道这段代码要在两个完全不同的环境里跑。

**TTS 参数建议**：
- `speed`: 1.0（正常语速）
- "啪，红屏"处加 `<emphasis level="strong">`
- "ReferenceError: window is not defined" 需 SSML `<say-as>` 或拼音标注

---

### 段落 4：MDC 被动约束降维打击（S4）

| 属性 | 值 |
|------|---|
| 场景 | S4 @SplitLayout |
| 情感 | 先否定传统解法 → 揭示更优方案 → 胜利感 |
| 预估时长 | 150s |
| 输出文件 | `voice-s04.wav` |
| 字数 | 约 200 字 |

**口播原文**：
> 传统解法？手动改代码，加 `typeof window === 'undefined'` 守卫。但这很蠢。你要跟 AI 反复拉扯，每次它都可能忘掉。更好的解法？被动约束。写一个 `.cursor/rules/remotion-ssr.mdc` 文件，里面只有一条规则：所有 Remotion 组件，访问浏览器全局对象前，必须检查环境。Cursor 读到这条规则，自动在生成的代码里加上守卫。你不用改一行代码，不用跟 AI 拉锯。看左边，没规则，Cursor 反复循环，不停报错。看右边，加了 MDC 规则，一次通过，直接出片。这就是约束的力量。不是人去盯 AI，是让规则去盯。

**TTS 参数建议**：
- `speed`: 1.0
- "但这很蠢"处加 `<emphasis>`（轻蔑语气）
- "一次通过，直接出片"处加重（胜利感）

---

### 段落 5：结尾 CTA（S5）

| 属性 | 值 |
|------|---|
| 场景 | S5 @OutroScene |
| 情感 | 总结 → 有力、号召感 |
| 预估时长 | 30s |
| 输出文件 | `voice-s05.wav` |
| 字数 | 约 130 字 |

**口播原文**：
> 掌握这套代码即视频的流程，你的后期效率能提升百倍。同样的内容，别人剪一天，你写一小时代码直接编译。而且，MDC 约束这套思路，不止用在 Remotion，任何 AI 辅助的场景都能套。想拿到本期完整的代码和规则模板？开源仓库在简介，自取。下期，我们讲一个更细的技术点：Whisper 毫秒级字幕卡点。如何让字幕精准跟上口播节奏，而且是自动的。关注，别错过。

**TTS 参数建议**：
- `speed`: 1.05（稍快，CTA 有力）
- "关注，别错过"处加 `<emphasis level="strong">`

---

## 术语 SSML 修正清单

以下技术术语可能被 TTS 引擎误读，需预处理：

| 术语 | 问题 | SSML 修正方案 |
|------|------|-------------|
| Remotion | 中文引擎可能读成"热摸森" | `<phoneme alphabet="ipa" ph="rɪˈmoʊʃən">Remotion</phoneme>` |
| SSR | 可能连读 | `<say-as interpret-as="characters">SSR</say-as>` → "S-S-R" |
| Cursor | 可能读成"库瑟" | `<phoneme alphabet="ipa" ph="ˈkɜːrsər">Cursor</phoneme>` |
| MDC | 可能连读 | `<say-as interpret-as="characters">MDC</say-as>` → "M-D-C" |
| React | 中文引擎可能音不准 | `<phoneme alphabet="ipa" ph="riˈækt">React</phoneme>` |
| useCurrentFrame() | 代码函数名 | 读作 "use Current Frame" 拆词 |
| useVideoConfig() | 代码函数名 | 读作 "use Video Config" 拆词 |
| Props | 可能读成"普洛普斯" | `<phoneme alphabet="ipa" ph="prɑːps">Props</phoneme>` |
| fps | 缩写 | `<say-as interpret-as="characters">fps</say-as>` → "F-P-S" |
| Node.js | 混合 | 读作 "Node" + 停顿 + "JS" |
| Puppeteer | 可能误读 | `<phoneme alphabet="ipa" ph="ˌpʌpəˈtɪr">Puppeteer</phoneme>` |
| window.innerWidth | 代码属性 | 读作 "window 点 inner Width" |
| npx remotion render | 命令 | 读作 "NPX remotion render"，NPX 逐字母 |
| 4K | 规格 | `<say-as interpret-as="characters">4K</say-as>` → "四K" |
| MP4 | 格式 | `<say-as interpret-as="characters">MP4</say-as>` → "M-P-4" |
| ReferenceError | JS 错误类型 | 读作 "Reference Error" 拆词 |
| typeof | JS 操作符 | 读作 "type of" 拆词 |
| .mdc | 文件扩展名 | 读作 "点 M-D-C" |

---

## 合成参数汇总

```python
# tts_selector 调用配置模板
common_config = {
    "language": "zh-CN",
    "preferred_provider": "doubao",
    "voice_id": "<待选定>",   # 需试听选择合适的男声/女声
    "output_format": "wav",
    "sample_rate": 44100,
    "bit_depth": 16,
}

segments = [
    {"id": "s01", "text": "...", "speed": 1.05, "emotion": "hook"},
    {"id": "s02", "text": "...", "speed": 0.95, "emotion": "explain"},
    {"id": "s03", "text": "...", "speed": 1.0,  "emotion": "narrative_climax"},
    {"id": "s04", "text": "...", "speed": 1.0,  "emotion": "persuasion"},
    {"id": "s05", "text": "...", "speed": 1.05, "emotion": "cta"},
]
```

---

## 总时长预估

| 段落 | 字数 | 预估时长 | 语速 |
|------|------|---------|------|
| S1 开头钩子 | ~150 字 | ~30s | 1.05x |
| S2 底层解密 | ~200 字 | ~45s | 0.95x |
| S3 SSR 踩坑 | ~220 字 | ~50s | 1.0x |
| S4 MDC 约束 | ~200 字 | ~45s | 1.0x |
| S5 结尾 CTA | ~130 字 | ~30s | 1.05x |
| **合计** | **~900 字** | **~200s（约 3 分 20 秒）** | |

> 注：脚本预估总时长 7 分 30 秒包含画面停留和动画时间，纯口播语音约 3-4 分钟属正常范围。

---

## 待决事项（需人工确认）

1. **音色选择**：需要试听豆包 TTS 可用 voice_type 列表，选择适合技术讲解的男声/女声
2. **API Key**：豆包 TTS 需要 `DOUBAO_SPEECH_API_KEY`（火山引擎控制台获取）
3. **SSML 支持度**：需确认豆包 TTS 对 `<phoneme>` 和 `<say-as>` 标签的支持程度，不支持时改用拼音注音方案
4. **是否需要试听多引擎对比**：可先用豆包生成一段 S1，不满意再切换 OpenAI TTS

---

## 落盘目录结构（待合成后填充）

```
content-library/ep02-video-render/06-tts/
├── README.md          # 本文件
├── assets/
│   ├── voice-s01.wav  # 待合成
│   ├── voice-s02.wav  # 待合成
│   ├── voice-s03.wav  # 待合成
│   ├── voice-s04.wav  # 待合成
│   └── voice-s05.wav  # 待合成
```
