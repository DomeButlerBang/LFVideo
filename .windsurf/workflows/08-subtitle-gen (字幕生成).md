---
description: 字幕生成 - 基于 TTS 音频或成片，用 Whisper 生成逐字时间戳，产出 SRT/VTT 字幕文件，可选 Remotion 弹跳字幕烧录。
---

# 字幕生成 Workflow (08-subtitle-gen)

基于 07 组装成片的音频轨，使用 Whisper 生成逐字级时间戳，产出 SRT/VTT 字幕文件。可选将字幕通过 Remotion 的 `@CaptionBurn` 组件烧录到画面中。

---

## 前置依赖

本工作流假设已完成 `/07-video-assembly`，已具备：
- 处于 `approved` 状态的 `content-library/<epNN-slug>/07-assembly/README.md`
- 渲染就绪的 MP4 成片（`video/out/<slug>.mp4`）

如果缺少上述输入，先提示用户回到 `/07-video-assembly`。

---

## 步骤

### 1. 提取音频轨

从成片 MP4 中提取音频（可使用 OpenMontage `audio_mixer.py` 的 `extract` 操作）：
```bash
# 使用 FFmpeg 提取
ffmpeg -i video/out/<slug>.mp4 -vn -acodec pcm_s16le -ar 16000 audio_for_whisper.wav

# 或使用 OpenMontage
audio_mixer.run({"operation": "extract", "video_path": "video/out/<slug>.mp4"})
```

### 2. Whisper 转录

使用 OpenMontage `transcriber.py` 进行语音识别：
- 模型推荐：`whisper-large-v3`（中文识别精度最高）
- 输出：逐字级时间戳 segments

```python
transcriber.run({
    "audio_path": "audio_for_whisper.wav",
    "language": "zh",
    "model": "large-v3",
    "word_timestamps": True
})
```

### 3. 生成字幕文件

使用 `subtitle_gen.py` 将转录结果转为字幕格式：

```python
subtitle_gen.run({
    "segments": transcriber_output["segments"],
    "format": "srt",           # 或 "vtt"、"caption_json"
    "max_chars_per_line": 20,  # 中文每行最多 20 字
    "max_lines": 2             # 最多双行
})
```

输出格式：
- **SRT**：通用字幕格式（B站、YouTube 均支持上传）
- **VTT**：Web 标准格式
- **caption_json**：Remotion 弹跳字幕专用 JSON

### 4. 字幕校对

逐条检查并修正：
- **术语修正**：Whisper 对技术术语可能识别错误（如 "Remotion" → "瑞莫森"），需手动校对
- **时间轴对齐**：检查字幕出现/消失时间是否与口播同步
- **断句合理性**：确保每行断句在语义完整处，避免词语被截断
- **标点符号**：补充必要的标点（Whisper 可能丢失）

### 5. 可选：Remotion 弹跳字幕烧录

如果需要将字幕烧录到画面中（而非外挂 SRT）：

使用 `remotion_caption_burn.py`：
```python
remotion_caption_burn.run({
    "caption_json": "captions.json",
    "style": "bounce",          # 弹跳字幕效果
    "font_size": 48,
    "font_color": "#FFFFFF",
    "stroke_color": "#000000",
    "stroke_width": 3,
    "position": "bottom_center"
})
```

生成的 Remotion 组件代码放入 `video/src/episodes/epNN-slug/` 中。

### 6. 落盘归档

字幕存放路径：
```
content-library/<epNN-slug>/08-subtitle/
├── README.md
├── assets/
│   ├── <slug>.srt              # SRT 字幕
│   ├── <slug>.vtt              # VTT 字幕
│   └── captions.json           # Remotion 弹跳字幕 JSON（可选）
```

`README.md` 格式：
```markdown
---
stage: 08-subtitle-gen
status: draft
source_workflow: /08-subtitle-gen
---

# epNN 字幕生成记录

## 配置
- Whisper 模型：large-v3
- 语言：zh
- 字幕格式：SRT + VTT

## 校对状态
- 术语修正：XX 处
- 时间轴调整：XX 处
- 总字幕条数：XXX 条

## 弹跳字幕（可选）
- [ ] 已烧录到成片
```

- 更新 `PIPELINE.md`：该期 08 列置 `draft`

### 7. 自我检查

- ❌ SRT/VTT 文件是否可正常加载播放？
- ❌ 技术术语是否全部校对？
- ❌ 字幕时间轴是否与口播同步（误差 < 0.3s）？
- ❌ 每行是否不超过 20 字？是否不超过双行？
- ❌ 如使用弹跳字幕，渲染后字幕是否清晰可读？

### 8. 交付与下一步

提示用户：
> 字幕就绪后（看板标 `approved`），可进入 `/09-bgm-mix` 添加背景音乐与混音。

---

## 关联文件

- 上游：`07-video-assembly (视频组装).md`
- 下游：`09-bgm-mix (BGM与混音).md`
- OpenMontage 工具：`tools/analysis/transcriber.py`、`tools/subtitle/subtitle_gen.py`、`tools/video/remotion_caption_burn.py`
