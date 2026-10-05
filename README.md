# my-skills

我在工作里攒下来的 AI Skill 合集。每个 Skill 是一份写给 AI 的操作说明（有的带脚本），装进 Claude Code、Codex 等工具后，AI 遇到对应任务会自动按它来做，比如清理 WPS 导出的 Markdown、给视频人脸打码、写项目总结。

**开始用：** 把想要的 Skill 目录复制或软链接到你所用工具的 skills 目录，然后正常提需求即可。以 Claude Code 为例：

```bash
git clone https://github.com/Canace22/my-skills.git
ln -s "$PWD/my-skills/clean-wps-markdown" ~/.claude/skills/clean-wps-markdown
```

Codex 换成 `~/.codex/skills/`。用软链接的好处是之后 `git pull` 就能拿到更新。

## 有哪些 Skill

| Skill | 什么时候用 | 需要额外装什么 |
|---|---|---|
| [clean-wps-markdown](clean-wps-markdown/SKILL.md) | 把 WPS / 金山文档导出的 Markdown 放进代码仓库前，修好错乱的标题序号、缩进，去掉打不开的图片 | Python 3 |
| [video-face-mosaic](video-face-mosaic/SKILL.md) | 给视频里的人脸批量打码，可以留一个人不打；手机拍的 HDR 视频也不会偏色 | Python 3、ffmpeg、`pip install deface opencv-python` |
| [anime-gothic-character](anime-gothic-character/SKILL.md) | 生成一张单人、全身、透明背景的哥特风动漫角色 PNG | macOS（校验脚本用 Swift）、AI 工具自带的生图能力 |
| [human-readable-docs](human-readable-docs/SKILL.md) | 写或改 README 等文档时，让 AI 站在"第一次来的人"的角度写 | 无 |
| [long-task-state](long-task-state/SKILL.md) | 任务长到要换新会话时，把进度写进 `STATE.md`，新会话读它就能接着做 | 无 |
| [ai-project-summary](ai-project-summary/SKILL.md) | 功能或 bug 修复做完后，生成一份改动总结提交进仓库 | 无 |
| [ai-editorial-board](ai-editorial-board/SKILL.md) | 文章写完想让人"审个稿"：9 个编辑角色分别给意见、分析标题，发布后拿数据复盘；只提意见不替你改写 | 无 |
| [product-intro-video](product-intro-video/SKILL.md) | 想给一个功能做介绍 / 演示视频：给它功能说明和几张截图，产出旁白脚本、分镜、套好设备外框的截图和能直接录屏的 PPT | Python 3、`pip install pillow`；做 PPT 时还要 `pip install python-pptx` |
| [mmorpg-mvp-from-scratch](mmorpg-mvp-from-scratch/SKILL.md) | 从零做一个能联机、能打怪、能做任务的网页多人 RPG 原型 | Node.js（生成的项目要用） |

## 使用前要知道

- **`ai-project-summary` 已改成目录结构。** 之前按旧说明手动建过 `ai-project-summary/` 目录的，删掉它，改成软链接仓库里的 `ai-project-summary/` 即可。
- **`mmorpg-mvp-from-scratch` 原本写给 claude.ai 用**，最后交付那步提到的 `SendUserFile` 和 Project 文档只有 claude.ai 上有。在 Claude Code、Codex 里用时，打包好的 zip 需要你按 AI 给的路径自己去拿，项目总结可以改用 `ai-project-summary` 写进仓库。
- **装了 Skill 不代表依赖也装好了。** 带脚本的 Skill（表格最后一列不是"无"的）第一次运行可能因为缺工具报错，按上表先装好。
- **各目录里的 `agents/openai.yaml` 只给 Codex 用**，决定它在界面里显示的名字和简介。用 Claude Code 可以忽略。

## 更多

- 更新记录：[CHANGELOG.md](CHANGELOG.md)
- 想新增或修改 Skill（包括让 AI 帮你维护这个仓库）：[AGENTS.md](AGENTS.md)
