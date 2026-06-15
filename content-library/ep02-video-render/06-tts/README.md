---
stage: 06-tts-synthesis
status: draft
source_workflow: /06-tts-synthesis
upstream_inputs:
  - 04-script/README.md (status: draft)
  - shared/docs/remotion-spec.md
engine: cosyvoice3 / piper-tts
model: Fun-CosyVoice3-0.5B / zh_CN-huayan-medium
---

# ep02 TTS 语音合成

> ⚠️ **重做版（对齐新 04 脚本）**：口播文本已按定稿 `tutorial.final.md` → 04 脚本的「教人用 Vibe Coding」两步主线**重新合成**——13 段一一对应 04 契约块 `sections[]`（旧 16 段 `范式/帧即状态/七阶段/三件套/编排器伪代码` 已删除，归 EP05/06）。`synthesize.py` 的 `NARRATION_SEGMENTS` 即为口播真相源的逐段拷贝；改 04 须同步改脚本再重合成。

## 引擎选型

脚本支持两种 TTS 引擎，默认使用 CosyVoice 3：

| 引擎 | 模型 | 采样率 | 部署方式 | 中文自然度 |
|------|------|--------|---------|-----------|
| **CosyVoice 3**（默认） | `Fun-CosyVoice3-0.5B` | 24000 Hz | 远程 GPU 服务 | ★★★★★ |
| Piper TTS（fallback） | `zh_CN-huayan-medium` | 22050 Hz | 本地 CPU | ★★☆☆☆ |

> 本次重做的样片用 **Piper（本地 CPU）** 合成,用于打通 07 组装的时间轴对齐;正式出片建议切 CosyVoice 3 重合成提升自然度(命令见下)。

### CosyVoice 3（推荐）

- **高自然度**：阿里通义语音团队开源模型，中文表现接近真人
- **多模式**：SFT 预训练音色 / 零样本克隆 / 自然语言控制
- **远程服务**：在 GPU 机器上部署 FastAPI 服务，本机通过 HTTP 调用

### Piper TTS（备选）

- **零成本**：无需 GPU、无需 API Key，完全本地推理
- **速度快**：13 段合成约 7 秒（CPU）
- **局限**：中文自然度机械，英文术语发音偏差（见下方术语表）

---

## 合成结果（13 段，对齐 04 sections[] id 1–13）

| 段落 ID | 04 段 | 对应场景 | 字数 | 时长 | 起点 | 文件 |
|---------|------|---------|------|------|------|------|
| S01_open | 1 | 开场钩子 / @IntroScene | 225 | 39.28s | 0:00 | `S01_open.wav` |
| S02_routes_intro | 2 | 选路线①·让 AI 摆出多路线 / @ConceptScene | 100 | 17.84s | 0:39 | `S02_routes_intro.wav` |
| S03_six_routes | 3 | 选路线①·六条路线 / @ConceptScene | 241 | 32.75s | 0:57 | `S03_six_routes.wav` |
| S04_pitfalls | 4 | 选路线②·逼 AI 给不适用+坑 / @TableScene | 323 | 50.36s | 1:30 | `S04_pitfalls.wav` |
| S05_why_remotion | 5 | 选路线②·为什么 Remotion / @ConceptScene | 155 | 25.89s | 2:20 | `S05_why_remotion.wav` |
| S06_vs_html | 6 | 选路线②·vs 复制粘贴 HTML / @SplitLayout | 202 | 24.94s | 2:46 | `S06_vs_html.wav` |
| S07_dispatch | 7 | 搭引擎①·配置分发 / @ConceptScene | 212 | 26.55s | 3:11 | `S07_dispatch.wav` |
| S08_config | 8 | 搭引擎①·配置即内容 / @TerminalScene | 132 | 18.58s | 3:38 | `S08_config.wav` |
| S09_fill_vs_build | 9 | 搭引擎①·造组件 vs 填数据 / @SplitLayout | 175 | 26.51s | 3:56 | `S09_fill_vs_build.wav` |
| S10_avatar | 10 | 搭引擎②·数字主持人基础版 / @ScreenshotScene | 153 | 27.90s | 4:23 | `S10_avatar.wav` |
| S11_ssr | 11 | 搭引擎②·SSR 避坑 / @SplitLayout | 274 | 34.24s | 4:51 | `S11_ssr.wav` |
| S12_render | 12 | 搭引擎②·一行出片 / @TerminalScene | 167 | 18.99s | 5:25 | `S12_render.wav` |
| S13_cta | 13 | 结尾 CTA / @OutroScene | 141 | 20.07s | 5:44 | `S13_cta.wav` |
| **合计** | **13 段** | | **2500 字** | **363.90s（6 分 04 秒）** | | |

> 时长为 Piper 实测（22050 Hz）。各段 `start` 为前序段时长累加，07 组装据此排时间轴。

---

## 运行方式

```bash
cd content-library/ep02-video-render/06-tts

# === CosyVoice 3（默认，需远程 GPU 服务） ===
python synthesize.py --engine cosyvoice3 --cosyvoice-url http://YOUR_GPU_SERVER:9880

# 也可通过环境变量配置
export COSYVOICE_URL=http://YOUR_GPU_SERVER:9880
python synthesize.py

# 可选参数：
#   --cosyvoice-mode sft|zero_shot|instruct2  推理模式（默认 sft）
#   --cosyvoice-spk "中文女"                   SFT 模式说话人 ID
#   --cosyvoice-instruct "用轻快的语气"        instruct2 模式指令
#   --cosyvoice-prompt-wav ref.wav             零样本克隆参考音频

# === Piper TTS（备选，本地运行） ===
pip install piper-tts
python synthesize.py --engine piper
```

产出在 `assets/` 目录，含 13 个 WAV 文件 + `manifest.json`。

---

## 术语发音说明（Piper 无 SSML，记录备忘）

以下术语在 Piper TTS 中文模型下发音存在偏差，**升级到 CosyVoice 3/豆包/OpenAI 时需加 SSML 修正**：

| 术语 | Piper 实际表现 | 升级时 SSML 方案 |
|------|--------------|----------------|
| Remotion | 可辨识但音调偏 | `<phoneme ph="rɪˈmoʊʃən">` |
| Explainer | 拆词不稳定 | 读作"Explainer"或按词拆 |
| SSR | 连读偏快 | `<say-as interpret-as="characters">` |
| MDC / mdc | 连读 | `<say-as interpret-as="characters">` |
| Vibe Coding | 偏快 | 按词拆读"Vibe Coding" |
| BUSL | 连读 | `<say-as interpret-as="characters">` |
| Manim / MoviePy / PixiJS / FFmpeg | 英文术语音调偏 | 按词拆读 |
| typeof window | 基本正确 | - |
| npx remotion render | 整体偏快 | 按词拆读 |
| Whisper | 基本正确 | - |

---

## 落盘目录结构

```
content-library/ep02-video-render/06-tts/
├── README.md           # 本文件（执行记录）
├── synthesize.py       # 合成脚本（NARRATION_SEGMENTS = 04 口播逐段真相源）
├── models/             # Piper 模型（gitignore，synthesize.py 自动下载）
└── assets/
    ├── manifest.json   # 合成清单（segment_id / duration / file_size）
    ├── S01_open.wav
    ├── S02_routes_intro.wav
    ├── S03_six_routes.wav
    ├── S04_pitfalls.wav
    ├── S05_why_remotion.wav
    ├── S06_vs_html.wav
    ├── S07_dispatch.wav
    ├── S08_config.wav
    ├── S09_fill_vs_build.wav
    ├── S10_avatar.wav
    ├── S11_ssr.wav
    ├── S12_render.wav
    └── S13_cta.wav
```

---

## 下一步

1. **试听审核**：人工试听各段 WAV，确认口播节奏和自然度（Piper 为样片，术语机械属预期）
2. **正式出片切 CosyVoice 3**：部署 GPU FastAPI 服务后 `--engine cosyvoice3` 重合成 13 段，替换 Piper 样片
3. **推进 07 组装**：将 `assets/*.wav` 作为口播音轨输入 07 视频组装阶段（已按本表起点排时间轴）
4. **Whisper 对齐**（EP03 字幕阶段）：对 WAV 做 Whisper 字级时间戳提取，驱动弹跳字幕

```json
{
  "stage": "06-tts-synthesis",
  "platform": "bilibili",
  "engines": ["cosyvoice3", "piper-tts"],
  "default_engine": "cosyvoice3",
  "rendered_with": "piper-tts",
  "total_segments": 13,
  "total_text_chars": 2500,
  "total_duration_seconds": 363.90,
  "segment_ids": [
    "S01_open", "S02_routes_intro", "S03_six_routes", "S04_pitfalls",
    "S05_why_remotion", "S06_vs_html", "S07_dispatch", "S08_config",
    "S09_fill_vs_build", "S10_avatar", "S11_ssr", "S12_render", "S13_cta"
  ],
  "cosyvoice3_config": {
    "model": "Fun-CosyVoice3-0.5B",
    "sample_rate_hz": 24000,
    "modes": ["sft", "zero_shot", "instruct2"]
  },
  "piper_config": {
    "model": "zh_CN-huayan-medium",
    "sample_rate_hz": 22050
  }
}
```
