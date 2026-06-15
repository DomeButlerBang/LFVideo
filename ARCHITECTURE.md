# AI IDE Workflows 项目架构设计 (Project Architecture)

本项目采用 **“全收敛单运行时 (Fully Converged Single-Runtime)”** 架构体系。我们将精品教程的视觉组件（如 Timeline、Table）完全融入 OpenMontage 内部，并将 OpenMontage 内置渲染器升级至最新的 React 19 / Remotion 4.0.470 协议，从而达到极简的数据闭环与工业级全自动声画同步。

---

## 1. 物理目录拓扑 (Physical Directory Topology)

```
ai-ide-workflows/ (项目根目录)
├── shared/                     # 跨 IDE 共享资源 (Single Source of Truth)
│   ├── roles/                  # 核心角色定义
│   ├── workflows/              # 13 阶段工作流真相源 (IDE 无关，纯 ASCII 文件名)
│   ├── docs/                   # 组件规格等
│   └── schemas/                # L0.5 严苛双核校验的 JSON Schema
├── .devin/workflows/           # [生成] Devin 工作流副本（由 sync 脚本物化，勿手改）
├── .windsurf/workflows/        # [生成] Windsurf 原生 Workflows 副本（/<slug> 调用）
├── .cursor/commands/           # [生成] Cursor slash 命令副本（/<slug> 调用）
├── scripts/sync_workflows.py   # 把 shared/workflows 物化到各 IDE 目录（--check 防漂移）
├── content-library/            # 内容库 (按 epNN 分类，纯净不含 React 模板代码)
│   └── ep02-video-render/      # 视频生产全生命周期文件 (01-07 阶段)
└── OpenMontage/                # [单运行时核心] Python 生产流水线与 React 19 渲染双引擎
    ├── tools/                  # 屏幕录制、音轨合成、AI 语音字幕工具 (Python)
    └── remotion-composer/      # React 19 / Remotion 4.0.470 全功能渲染器 (合并了我们所有的自定义场景)
```

---

## 2. 单运行时收敛设计 (Converged Single Runtime)

通过将外部独立视频工程并入 OpenMontage，我们消除了两个运行时（React 18 vs React 19）的版本代差，获得了统一的高效生产力：

| 维度 | `OpenMontage/remotion-composer/` (升级合并后) |
|:---|:---|
| **React 版本** | **React 19.2.6** (全线升级) |
| **Remotion 版本** | **4.0.470** (全线升级) |
| **组件特性** | 通用 Explainer 模板 (数据图表、ProgressBar) + 精品教程模板 (TimelineScene、TableScene) 共存 |
| **主打场景** | 全片自动化渲染卡点、口播配音合成、GitHub 开源精品 React 模板库 |

### 收敛决策的核心优势
1. **100% 自动卡点**：直接利用 OpenMontage 内置的语音逆向对齐（TTS + WhisperX word-level 时间戳），React 场景自动根据音频长度适配帧数，彻底解决**长场景死时间、画音不同步**等质量硬伤。
2. **零启动开销**：我们无需从头手写打字机（TerminalScene）、页面局部放大（ScreenshotScene）、产品宣传卡（ProductReveal）等基础工程组件，直接调用 OpenMontage 成熟的高质量基础件作为杠杆。
3. **极速调试 (DX)**：在 `OpenMontage/remotion-composer/` 目录下运行 `npm run start` 即可在本地启动 Remotion Studio。在开发时，它同时支持通过 `cuts[i].type` 渲染我们移植进去的五大自定义精品场景（Intro, Outro, Concept, Timeline, Table）。

---

## 3. 全自动流水线数据流 (Automated Pipeline Data Flow)

```
[1. 口播脚本 Markdown]
         │
         ▼
[2. OpenMontage TTS 语音生成] ──► 生成 scene_N.mp3 分段音轨
         │
         ▼
[3. WhisperX 时间戳提取]      ──► 提取精确到单词/字级的 millisecond 标记
         │
         ▼
[4. Verify Scene Pacing]      ──► 自动匹配口播时间与 React 动作物理时长，报错拦截静死屏
         │
         ▼
[5. Remotion 自动渲染]        ──► npx remotion render Explainer --props .remotion_props.json
         │
         ▼
     [ 4K MP4 完片 ]
```

---

## 4. 单一事实源原则 (Single Source of Truth)

- **角色定义**：所有角色（如 `copywriter`, `strategist`）仅在 `shared/roles/` 维护一份 Markdown 文件。
- **工作流定义**：13 阶段工作流仅在 `shared/workflows/<slug>.md` 维护一份（IDE 无关，纯 ASCII 文件名，中文名在 frontmatter `title`）。各 IDE 实际调用的副本由 `scripts/sync_workflows.py` **生成**，不手改：
  - **Devin**：`.devin/workflows/<slug>.md`
  - **Windsurf**：`.windsurf/workflows/<slug>.md`（原生 Workflows，`/<slug>` 调用）
  - **Cursor**：`.cursor/commands/<slug>.md`（slash 命令，`/<slug>` 调用）
  - 改完真相源后跑 `python scripts/sync_workflows.py`；`--check` 模式（已接入 pre-commit）保证生成副本永不漂移。
- **IDE 规则适配（rules，后续 PR 收敛）**：
  - **Cursor**：通过 `.cursor/rules/*.mdc` 进行被动约束，仅做**路径指向与适配**，不复制角色内容。
  - **Windsurf**：通过 `.windsurf/rules/` 进行主动约束，同样采用相对引用指向 `shared/roles/`。

---

## 5. React/Remotion 开发与渲染规范 (Robustness & Rendering Guidelines)

### 5.1 自适应自愈模式 (Self-Healing Design Pattern)
为了保证 Remotion Studio 预览界面的 100% 稳定性，防止在预览缺省、空配置、或临时资产时的崩溃：
- **媒体组件守卫 (Media Guard)**：所有的原生多媒体渲染组件（如 `<OffthreadVideo>`、`<Video>`、`<Audio>`）在渲染前**必须进行 `src` 空校验与有效性守卫**。
- **视频占位降级 (Video Fallback)**：当 `videoSrc` 或 `backgroundSrc` 为空/未配置时，必须降级渲染高对比度、暗色的 `div` 占位框（如 `[视频占位符: src 未配置]`），而非直接渲染空 `src` 的视频组件（空 `src` 会导致浏览器抛出 `MediaPlaybackError` 触发红屏崩溃）。
- **音频零渲染守卫 (Audio Guard)**：所有的背景音轨、口播音轨组件（如 `Soundtrack`）在 `src` 为空或无效时，应立即 `return null`。

### 5.2 渲染分辨率规范 (Rendering Resolution Standard)
- **目标分辨率**：本频道视频渲染和导出统一规范为 **1080p 高清（1920×1080 @ 30fps）**，无需渲染 4K。
- **核心考量**：1080p 在保证画质清晰度的前提下，能缩短数十倍的 Puppeteer 后台多核截图与 FFmpeg 合成时间，极大提高 AI 流水线自动迭代与成片效率。

