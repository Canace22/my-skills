---
name: run-web-project-locally
description: "把第三方 GitHub / web 项目拉到本地跑起来给用户看效果：clone、读 README 确认启动方式、装依赖、后台起 dev server、curl 验证，最后汇报访问地址和操作说明。当用户发来 GitHub 链接说「拉下来跑一下」「看看效果」「本地跑起来」时使用。"
---

# 拉取第三方项目本地跑起来（"帮我跑一下看看效果"）

## 触发条件

- 用户发来 GitHub 链接 / 项目名，要求「拉下来」「跑一下」「看看效果」
- 用户想看某个开源 demo / 实验项目的实际效果

## 工作流（按序执行）

1. **clone 到约定目录** — 先看用户有没有约定实验项目放哪（AGENTS.md、记忆、之前的对话）。很多人会把正式工作和实验/第三方项目分开放，别 clone 进正式工作目录。没有约定就问一句：
   ```bash
   git clone <url> <实验项目目录>/<ProjectName>
   ```
2. **读 README 确认启动方式** — 并行读 `README.md` + `package.json`（或 pyproject/setup 等），找 Quick start / 启动命令 / 端口号。README 的 Controls / 操作说明部分顺便读一下，后面汇报要用。
3. **装依赖** — 常见 `npm install`。注意：
   - 一般几十秒到 1-2 分钟能完成，给足超时（5 分钟左右）
   - 大依赖（如 PySide6、机器学习包）放后台跑，完成后再继续，别让前台超时把它杀掉
   - `npm audit` 提示一般不影响运行，忽略即可
4. **后台起 dev server** — dev server 是长驻进程，必须放后台跑，并盯着输出等 ready 信号（`Local:`、`ready in`、`localhost`）：
   ```bash
   cd <proj> && npm run dev
   ```
   Vite 默认 `http://127.0.0.1:5173`；其他框架看 README/输出。
5. **验证服务真的活了** — 看到 ready 输出后，`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<port>/` 应为 200。别只靠进程启动就汇报。
6. **汇报给用户**：
   - 可访问 URL（浏览器直接打开）
   - 这是什么东西（读 README 一句话说清）
   - 核心操作/按键表（让用户能直接玩，不读文档）
   - 提一下特别值得看的功能点

## 边界

- clone、装依赖、起服务、curl 验证都只是运行，不改项目代码
- 项目**跑不起来、需要改代码或配置才能跑**时，先告诉用户哪里不行、打算怎么改，确认后再动

## 用户说「一堆错误」时

dev server 正常、curl 200，但用户说浏览器里一堆错误，问题几乎都在浏览器端：

- **最快解法：先让用户 `Cmd+Shift+R` 硬刷新**。依赖重新预构建后，已打开的旧页面会卡在旧依赖上，刷新大概率直接好。
- **确认端口上是哪个项目**：多个 dev server 同时跑时 Vite 会自动换端口（5173 → 5174 → 5175），汇报时用实际端口，并 curl 首页的 `<title>` 确认。
- 还不行，按 `vite-dev-server-troubleshooting` 这个 Skill 的顺序排查。
- 用户发的是控制台截图而你看不了图，在 macOS 上用 `image-ocr-macos` 这个 Skill 把文字读出来，别盲猜。

## 注意事项

- dev server 是长驻进程：前台跑会一直挂着占住调用，必须放后台
- 别只信进程输出就报「跑起来了」——先 curl 一次拿到 HTTP 状态再汇报
- 老项目可能用 `npm run start` / `npm run serve` / Python `http.server`，以 README 为准
- README 很长时先读前 100 行（Quick start + Controls 通常在前部），不要整篇通读
- 汇报操作提示时给「按键 → 动作」表比长篇描述高效，用户看完就能玩
