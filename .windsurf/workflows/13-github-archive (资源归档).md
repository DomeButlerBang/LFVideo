---
description: 资源归档 - 清理开发过程中的临时文件与缓存，整理出干净、优雅的开源代码，打包 Prompts 与 Rules，撰写面向社区的高质量 README，并将配套资源同步至 GitHub 仓库。
---

# 资源归档 Workflow (13-github-archive)

本工作流由**执行工程师**角色执行。其目的是在视频成片并分发（12）之后，**对 GitHub 资源库进行专业化整理与发布**，为观众提供极佳的"课后配套开源代码与规则模板"下载体验。

---

## 前置依赖

本工作流假设已完成 `/12-distribute-adapt`，且视频已基本就绪或已发布。

---

## 步骤

### 1. 清理临时开发文件 (Sanitization)

- 检查前期验证 Demo 或实际开发过程中产生的临时文件、日志和缓存。
  - 必须清理的项：`node_modules/`（不应提交）、`.env` 敏感配置、临时生成的 test/ 乱码代码、Remotion 渲染缓存等。
  - 通过配置 `.gitignore` 防止临时文件被推送到远程。

### 2. 规范化开源代码结构

按照项目约定的标准配套结构，将代码整理到 `content-library/<epNN-slug>/` 下：
```
content-library/<epNN-slug>/
├── README.md                # 观众看到的开源下载引导
├── .cursorrules             # 配套 Cursor 规则 (若有)
├── .windsurf/
│   └── rules                # 配套 Windsurf 规则 (若有)
├── prompts/                 # 核心 Prompt 整理
│   ├── 01-hook.txt
│   └── 02-scaffold.txt
└── code/                    # 最简能跑通的示例代码 (精简、美观、有注释)
```

### 3. 撰写面向社区的 README.md

在 `content-library/<epNN-slug>/` 根目录下，撰写一份具备生产力工具质感的 `README.md`，包含：
- **这期视频能干什么**：Demo 功能介绍
- **怎么在本地跑起来**：克隆、安装依赖、启动命令
- **核心 Prompts 复制区**：方便观众直接复制
- **Rules 使用说明**：如何把 `.cursorrules` / `rules` 导入他们自己的项目

### 4. 代码审查与验收 (Code Review)

- 用 AI 协助或自己审查：
  - 代码中是否含有写死的本地路径？
  - 代码中是否包含未删除的敏感 API-Key？（绝对禁止提交）
  - 注释是否清晰，能引导观众自己改动？

### 5. Git 提交与同步
- 将文件推送到 GitHub 对应仓库。
  - 编写专业的 Git Commit 信息（如 `feat(ep01): archive companions and prompt rules`）。
  - 执行 `git add` / `git commit` / `git push`（如有安全指令，先运行测试再 push）。

### 6. 输出归档记录

在 `content-library/<epNN-slug>/13-archive/README.md`（或 `README.md` 本身）中打上归档标识：
```markdown
---
stage: 13-github-archive
status: draft
source_workflow: /13-github-archive
---

# epNN 配套资源归档记录

- **GitHub 资源路径**：https://github.com/your-username/ai-ide-workflows/tree/main/content-library/epNN-slug
- **沉淀的开源代码**：React / Node / Python
- **沉淀的 Rules**：Cursor .cursorrules / Windsurf Rules
- **是否已做安全审查**：✅（无 API key，无本地私有路径）
- **同步状态**：已 Push
```

### 7. 归档状态更新
- 写入 `content-library/<epNN-slug>/13-archive/README.md`。
- 在 `content-library/PIPELINE.md` 中的 13 列置为 `approved`（完结）。

---

## 关联文件

- 角色：`shared/roles/execution/engineer(执行工程师).md`
- 上游：`12-distribute-adapt (分发适配).md`
