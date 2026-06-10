---
description: BGM与混音 - 为成片选配背景音乐、音效，执行口播/BGM/音效多轨混音与响度标准化。
---

# BGM与混音 Workflow (09-bgm-mix)

为 07 组装成片选配背景音乐（BGM）和音效（SFX），使用 OpenMontage `audio_mixer` 完成多轨混音：口播人声为主、BGM 自动闪避（ducking）、整体响度标准化至 -14 LUFS（B站推荐）。

---

## 前置依赖

本工作流假设已完成 `/08-subtitle-gen`，已具备：
- 处于 `approved` 状态的 `content-library/<epNN-slug>/07-assembly/README.md`
- 渲染成片 MP4
- 字幕文件（08 阶段产出）

如果缺少上述输入，先提示用户回到对应上游阶段。

---

## 步骤

### 1. 分析音乐需求

根据视频内容和节奏规划 BGM 方案：

| 段落 | 情绪 | BGM 类型 | 音量策略 |
|------|------|---------|---------|
| 开头钩子 | 紧张/好奇 | 电子/科技感 | 中等，口播开始后 ducking |
| 核心对比 | 严肃/专业 | 轻柔背景 | 低音量 ducking |
| 实操演示 | 专注/节奏 | Lo-fi / Minimal | 极低或静音 |
| 结尾CTA | 激昂/鼓舞 | 渐强收尾 | 口播结束后渐强 |

### 2. 选择背景音乐

使用 OpenMontage 音乐工具搜索/生成 BGM：

**免费素材库**（推荐优先）：
```python
# Pixabay 免版税音乐
pixabay_music.run({
    "query": "technology ambient",
    "duration_range": [180, 600],  # 3-10 分钟
    "mood": "inspiring"
})
```

**AI 生成**（定制化需求）：
```python
# Suno AI 音乐生成
suno_music.run({
    "prompt": "轻柔科技感背景音乐，适合技术教程视频，BPM 90-110",
    "duration": 300
})

# MusicGen 本地生成
music_gen.run({
    "description": "ambient electronic, soft synth pads, tech tutorial background",
    "duration": 300
})
```

**其他素材源**：
- `freesound_music.py`：Freesound 音效库（适合 SFX）

### 3. 音效设计（可选）

为关键节点添加音效：
- 场景切换：轻微 "whoosh" 过渡音
- 错误示例（❌）：低沉警告音
- 正确示例（✅）：清脆确认音
- 数据/表格入场：打字机/数据流音效

### 4. 多轨混音

使用 `audio_mixer.py` 的 `full_mix` 模式一步完成：

```python
audio_mixer.run({
    "operation": "full_mix",
    "narration_paths": ["voice-s01.wav", "voice-s02a.wav", ...],
    "music_path": "bgm.mp3",
    "sfx_tracks": [
        {"path": "whoosh.wav", "start_time": 12.5},
        {"path": "error.wav", "start_time": 45.0}
    ],
    "ducking": {
        "enabled": True,
        "duck_amount_db": -12,    # BGM 口播时降 12dB
        "attack_ms": 200,
        "release_ms": 500
    },
    "normalize_lufs": -14,         # B站推荐响度
    "output_path": "final_audio.wav"
})
```

关键参数：
- **Ducking**：口播时 BGM 自动降低 12-15dB，口播间隙恢复
- **响度标准化**：-14 LUFS（B站/YouTube 推荐）
- **淡入淡出**：BGM 头尾各 2s fade

### 5. 合并音视频

将混音后的音频替换成片原音轨：
```bash
ffmpeg -i video/out/<slug>.mp4 -i final_audio.wav \
  -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 \
  video/out/<slug>-mixed.mp4
```

### 6. 试听检查

- 口播清晰度：BGM 是否压制了人声？（ducking 不足则增大 duck_amount_db）
- BGM 节奏：是否与画面切换节奏匹配？
- 音效时机：SFX 是否精准对齐画面事件？
- 首尾处理：开头 BGM 淡入是否自然？结尾是否干净收尾？
- 响度一致：全片响度是否稳定，无突然跳变？

### 7. 落盘归档

```
content-library/<epNN-slug>/09-bgm/
├── README.md
├── assets/
│   ├── bgm.mp3              # 原始 BGM
│   ├── sfx/                  # 音效文件夹
│   └── final_audio.wav       # 混音后音频
```

`README.md` 格式：
```markdown
---
stage: 09-bgm-mix
status: draft
source_workflow: /09-bgm-mix
---

# epNN BGM与混音记录

## BGM 信息
- 来源：Pixabay / Suno AI / MusicGen
- 曲名/ID：xxx
- 时长：XXX 秒
- 许可：CC0 / 免版税

## 混音参数
- Ducking：-12dB（attack 200ms / release 500ms）
- 标准化响度：-14 LUFS
- 音效数量：X 个

## 成片路径
- `video/out/<slug>-mixed.mp4`
```

- 更新 `PIPELINE.md`：该期 09 列置 `draft`

### 8. 自我检查

- ❌ BGM 版权是否清晰（免版税/CC0/自生成）？
- ❌ 口播是否始终清晰可辨，未被 BGM 压制？
- ❌ 全片响度是否在 -14 ± 1 LUFS 范围内？
- ❌ 音效是否精准对齐画面？
- ❌ 首尾淡入淡出是否自然？

### 9. 交付与下一步

提示用户：
> 混音成片就绪后（看板标 `approved`），可进入 `/10-cover-gen` 生成多平台封面图。

---

## 关联文件

- 上游：`08-subtitle-gen (字幕生成).md`
- 下游：`10-cover-gen (封面生成).md`
- OpenMontage 工具：`tools/audio/audio_mixer.py`、`tools/audio/pixabay_music.py`、`tools/audio/suno_music.py`、`tools/audio/music_gen.py`、`tools/audio/freesound_music.py`
