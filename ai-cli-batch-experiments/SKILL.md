---
name: ai-cli-batch-experiments
description: "批量生成实验流程：同一 prompt 交给多个 AI 编码 CLI（claude/codex）各跑 N 次，把产物（HTML/文件）当数据采集——清洗、提取特征、统一视口截图、手填标准化标注，只交付数据不下结论。当用户说「跑实验」「批量生成」「风格趋同」「AI 工具对比」，或给了一份定义实验流程的 TASK.md 时使用。"
---

# AI CLI 批量生成实验

## 何时用

用户要「同一个 prompt 给不同 AI 编码工具各生成 N 次」并比对产物（典型：页面风格趋同实验）。
通常由一份 TASK.md 定义流程，且明确「只做数据采集和特征提取，不要下结论」。

## 实验前提（不成立就先停，别自行替换）

- 每个 CLI 都要可用；非交互参数用 `--help` 确认真实用法，不猜
- CLI 认证要真的能跑（见陷阱 1：claude OAuth 过期是高频故障）
- Python + Playwright + 浏览器可用（`pip install playwright`，再 `playwright install chromium`；装不上浏览器时脚本会回退到系统 Chrome）

## 核心原则

1. **文件名 = 数据主键**：严格按实验命名规范（如 `<组>-<页面>-<工具>-<次数>.html`），后续脚本靠文件名解析组别/工具，命名错了整行数据作废。
2. **每次生成必须全新会话**：同会话连跑 N 次会让后几次参考第一次，实验作废。各 CLI 的保证方式见流程 3。
3. **只重跑「非合法输出」**：输出不是完整文件（缺 `<!DOCTYPE`/`</html>`）才重跑；「不好看」绝不重跑。
4. **手填列要标准化**：结构相同必须写成完全一致的字符串（如 `hero+3卡+CTA`），否则没法统计撞车。
5. **不下结论**：交付物是数据 + 截图 + 事实说明；相似度判断留给用户，别替用户评价「看起来很像」。
6. **按阶段门控**：TASK.md 说「跑完第一段停下来等确认」，就停；被阻塞时先交付已完成部分并说清阻塞原因，不干等。

## 流程

1. **环境检查**：`claude --version`、`codex --version`、playwright 可用性；`--help` 确认非交互参数（claude 用 `-p`，codex 用 `exec`）。CLI 参数以实际 `--help` 为准，别凭记忆猜。
2. **冒烟测试**（关键，防 6 次生成全废）：先各跑一个 hello 级 prompt 输出到 /tmp，确认认证和输出正常，再开始正式批量。claude 403 / codex 报错在冒烟阶段暴露最划算。
3. **批量生成**：原始 stdout 和 stderr 分开存 `raw/`（如 `raw/<name>.txt` + `.err`）；某次失败就重跑那一次，不留半截文件。
   - claude：`claude -p "<prompt>" --max-turns 1 --output-format text` —— print 模式每次天然全新会话、不落盘（`--no-session-persistence` 不是唯一保证方式；2026-08-09 实测不带该参数、仅靠每次独立进程也满足独立生成）
   - codex：`codex exec --skip-git-repo-check "<prompt>"` —— exec 每次天然新会话（resume 是独立子命令）；非 git 目录必须加 skip 参数
4. **清洗**：`python3 scripts/clean_output.py raw/X.txt runs/X.html` —— 剥 ```html 围栏、截取 `<!DOCTYPE`…`</html>`、打印起止片段校验。
5. **提取特征 + 手填**：跑项目自带 extract 脚本生成 CSV；`布局骨架` 这类脚本填不了的列，逐个看 HTML 结构手填，同结构必须同字符串。
6. **截图**：`python3 scripts/screenshot_html.py` —— 统一视口宽度（如 1280）、整页截图、与 runs 同名。
7. **交付**：CSV + 截图 + 一句话说明（有没有重跑、为什么、怎么保证独立会话）；到阶段边界停下等确认。

## 陷阱

1. **claude -p 403**：`claude auth status` 显示已登录、交互界面正常，但 `claude -p` 报 403 "Request not allowed"——多半不是 token 过期，而是网络受地区限制，而执行命令的 shell 没加载用户在 `.zshrc` 里配的代理。快速诊断：`env | grep -i proxy`（空 = 代理没带上）→ 用 `curl -s -o /dev/null -w '%{http_code}' https://api.anthropic.com/v1/models` 对比直连和加 `-x <代理地址>` 的结果。修复：把代理的 export 也写进非交互 shell 会读的文件（如 `~/.bash_profile`、`~/.bashrc`）。**不要**急着 `claude auth login` 或去动凭证文件——本地凭证显示过期不代表服务端失效。**实验场景不要换别的后端顶替被测 CLI**——换后端等于换了被测变量，数据作废；宁可先修好再跑。
2. **codex 非 git 目录拒绝运行**：报 "Not inside a trusted directory and --skip-git-repo-check was not specified"，加 `--skip-git-repo-check`。
3. **Playwright 浏览器版本不匹配**：报 "Executable doesn't exist at .../chromium_headless_shell-XXXX" 时，两级兜底：① ms-playwright 缓存里的完整 chromium（`find ~/Library/Caches/ms-playwright -name "*chrome*"` 确认后 `launch(executable_path=<真实存在的完整chromium>, headless=True)`）；② **macOS 系统 Chrome**：`launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless=True)`——2026-08-09 实测最稳，缓存 chromium 与 playwright 包协议不匹配时仍可用（scripts/screenshot_html.py 已内置三级自动探测：默认 → 缓存 chromium → 系统 Chrome）。
4. **文件搜索可能漏掉刚重建的目录/文件**：实验目录可能刚被用户重建（如 setup 脚本补回 prompts/）。第一次没找到、用户说「再看看」时，用 `find` / `mdfind` 复核，别直接认定缺失。
5. **codex stdout 可能带杂讯**（如 "tokens used" 统计行）：清洗脚本按 `<!DOCTYPE`/`<html` 截取即可免疫；排查输出问题时先分开 stdout/stderr，别急着 `2>&1` 混流。
6. **清理脚本别写死在实验目录**：`clean_output.py` / `screenshot_html.py` 是 skill 自带 scripts/，新实验直接调用或复制。

## 支持文件

- `scripts/clean_output.py` — 剥围栏 + 截取完整 HTML 的清洗器
- `scripts/screenshot_html.py` — 自动探测 chromium 的统一视口整页截图
- `references/experiment-layout-example.md` — 一个实验目录约定的示例（页面风格趋同实验）
