# 更新记录

按日期倒序。这个仓库不发版本号，以提交日期为准。会影响已安装用户的变化标 **注意**。

## 2026-10-05

- 用 `sync-local-skills` 从本机 agent 同步进 10 个 Skill，并按仓库约定整理（只留 name/description、去掉本机路径和个人项目信息、把各 agent 专用的工具写法改成通用说法）：
  - 来自 Cursor：`web-style-clone`
  - 来自 Hermes：`ui-styling-patterns`、`vite-dev-server-troubleshooting`、`run-web-project-locally`、`game-asset-integration`、`media-processing`、`image-ocr-macos`、`ai-cli-batch-experiments`、`web-novel-creation`、`macos-automator-service-fix`
- 新增 `sync-local-skills`：扫描本机各 AI agent（Claude Code、claude.ai 同步、Codex、Cursor、Hermes 等）里自己写的 Skill，挑选后同步进仓库，并检查 frontmatter、本机路径和疑似密钥。同步记录存在 `sync-local-skills/synced.json`，同步后在仓库里整理过的 Skill 不会被一直当成有改动。
- 从 Codex 的个人 Skill 目录同步 `meshy-blender-character`（游戏角色与动物伙伴制作），保留脚本、参考资料和已有 Codex 界面配置。
- 新增 `human-readable-docs`：写 README 等文档时切换到新人视角。
- 新增 `anime-gothic-character`：生成单人透明背景的哥特风动漫角色，附带透明度校验和抠色脚本（Swift，仅 macOS）。
- 新增 `long-task-state`：长任务落盘 `STATE.md`，新会话冷启动续接。
- 文档重写：README 只保留上手信息，新增本文件和 `AGENTS.md`。
- 从 claude.ai 同步进来：`ai-editorial-board`（9 角色审稿）、`product-intro-video`（功能介绍视频脚本 + 设备外框 + 录屏用 PPT）、`mmorpg-mvp-from-scratch`（网页多人 RPG 原型的任务编排）。
- **注意** `ai-project-summary` 从单文件 `ai-project-summary.md` 改为 `ai-project-summary/SKILL.md`，并修好 frontmatter 分隔线；正文补了写作原则。按旧说明手动建过目录的，换成软链接仓库目录。

## 2026-08-13

- `clean-wps-markdown`：新增 `--renumber-headings`，把标题重编为 `一、` / `1、` / `1.1` 三级序号。

## 2026-08-12

- 新增 `clean-wps-markdown`：清理 WPS / 金山文档导出的 Markdown。
- **注意** `clean-wps-markdown`：默认删除图片（WPS 图片链接带权限，导出后通常打不开）。要保留原链接加 `--keep-images`，要下载到本地用 `--download-images <目录>`。

## 2026-08-01

- 新增 `video-face-mosaic`：视频人脸批量打码，可保留指定人物，自动处理 HDR。

## 2026-06-10

- 新增 `ai-project-summary`（单文件形式，见 README「使用前要知道」）。
