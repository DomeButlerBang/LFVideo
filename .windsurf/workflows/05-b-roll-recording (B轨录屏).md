---
description: B轨录屏 - 按 03 视听蓝图的 zoom_crop_directives 录制 IDE/终端操作演示，产出可直接嵌入 Remotion @VideoSlot 的 B 轨素材。
---

# B轨录屏 Workflow (05-b-roll-recording)

按 03 蓝图中标注 `@VideoSlot` 的场景，录制真实 IDE / 终端操作演示。录屏素材在 07-video-assembly 阶段嵌入 `@VideoSlot` 组件；若录屏缺失，07 阶段将自动降级使用 A 轨兜底方案（`fallback_a_track`）。

---

## 前置依赖

本工作流假设已完成 `/04-script-draft`，已具备：
- 处于 `approved` 状态的 `content-library/<epNN-slug>/04-script/README.md`
- 处于 `approved` 状态的 `content-library/<epNN-slug>/03-plan-bilibili/README.md`（含 `zoom_crop_directives` 和 `fallback_a_track`）

如果缺少上述输入，先提示用户回到对应上游阶段。

---

## 步骤

### 1. 提取录屏清单

从 `03-plan-bilibili/README.md` 的 JSON 校验块中提取所有 `@VideoSlot` 场景：
- 场景编号（如 S5a、S5b、S5c）
- `zoom_crop_directives`：录屏时的裁剪/缩放指令
- `src` 占位描述：录屏内容说明
- `fallback_a_track`：A 轨兜底方案（用于判断优先级）

输出录屏任务清单表：

| # | 场景 | 录屏内容 | zoom_crop | 预估时长 | 优先级 |
|---|------|---------|-----------|---------|--------|
| 1 | S5a-left | IDE录屏—AI从零手写组件 | `crop: editor_only` | 25s | 高（有 A 轨兜底但实录更真实） |
| ... | ... | ... | ... | ... | ... |

### 2. 准备录屏环境

- 打开目标项目工程（如 `OpenMontage/remotion-composer`）
- 调整 IDE 主题为深色（统一视觉风格）
- 字体大小设为 ≥16px（确保 1080p 下可读）
- 关闭无关 Tab、通知和系统弹窗
- 如使用 OpenMontage 工具，可调用 `screen_capture_selector.py` 选择最佳录屏方案

### 3. 逐条录制

对每条录屏任务：

1. **设置裁剪区域**：按 `zoom_crop_directives` 配置屏幕录制区域
   - `crop: editor_only` → 仅录代码编辑区
   - `crop: terminal_only` → 仅录终端区域
   - `crop: full_ide` → 录完整 IDE 窗口
2. **执行操作**：按脚本 `[画面]` 描述执行真实操作
3. **录制**：使用 OBS / OpenMontage `screen_recorder.py` / `cap_recorder.py` 录制
4. **命名规范**：`b-<scene_id>.mp4`（如 `b-s5a-left.mp4`、`b-s5b-right.mp4`）

### 4. 素材后处理

- 裁剪首尾空白（保留操作核心部分）
- 统一分辨率：1920×1080（或按 zoom_crop 裁剪后的目标分辨率）
- 统一帧率：30fps
- 可选：使用 `video_trimmer.py` 或 `silence_cutter.py` 去除静默段

### 5. 落盘归档

素材存放路径：
```
content-library/<epNN-slug>/05-b-roll/
├── README.md          # 录屏清单与状态
├── assets/
│   ├── b-s5a-left.mp4
│   ├── b-s5a-right.mp4
│   ├── b-s5b-left.mp4
│   ├── b-s5b-right.mp4
│   └── b-s5c.mp4
```

`README.md` 格式：
```markdown
---
stage: 05-b-roll-recording
status: draft
source_workflow: /05-b-roll-recording
---

# epNN B轨录屏素材清单

| 文件名 | 对应场景 | 时长 | 分辨率 | 状态 |
|--------|---------|------|--------|------|
| b-s5a-left.mp4 | S5a 左侧（从零手写） | 25s | 1920×1080 | ✅ 已录 |
| ... | ... | ... | ... | ... |

> 未录制的场景将在 07 组装阶段使用 A 轨兜底方案（`fallback_a_track`）渲染。
```

- 更新 `PIPELINE.md`：该期 05 列置 `draft`

### 6. 自我检查

- ❌ 所有 `@VideoSlot` 场景是否都有对应录屏（或明确标注使用 A 轨兜底）？
- ❌ 录屏分辨率/帧率是否统一？
- ❌ 录屏内容是否与脚本 `[画面]` 描述一致？
- ❌ 文件命名是否符合 `b-<scene_id>.mp4` 规范？

### 7. 交付与下一步

提示用户：
> 录屏素材就绪后（看板标 `approved`），可并行执行 `/06-tts-synthesis` 生成口播音频，然后进入 `/07-video-assembly` 组装成片。

---

## 关联文件

- 上游：`04-script-draft (脚本撰写).md`、`03-video-planning-bilibili (B站视听策划).md`
- 下游：`07-video-assembly (视频组装).md`
- OpenMontage 工具：`tools/capture/screen_recorder.py`、`tools/capture/cap_recorder.py`、`tools/capture/screen_capture_selector.py`
