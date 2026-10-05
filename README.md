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
| [meshy-blender-character](meshy-blender-character/SKILL.md) | 按参考图做游戏角色或动物伙伴，用 Meshy / 腾讯混元 3D 生成，再到 Blender 整理、做动画并接入游戏 | Blender、Blender MCP 插件、生成服务账号；脚本需要 Python 3，附带 MCP 客户端还需要 uv（运行命令自动装依赖） |
| [sync-local-skills](sync-local-skills/SKILL.md) | 在 Claude Code、Codex、Cursor、Hermes 等工具里自己写了 Skill，想收进这个仓库：先列出哪些还没进仓库、哪些和仓库不一致，你挑完再拷进来并整理好 | Python 3 |
| [web-style-clone](web-style-clone/SKILL.md) | 想让页面"照着这个网站的感觉做"：拆出参考网页的布局、配色、字体、间距和动效，整理成设计变量再写代码，不抄素材和 logo | 无 |
| [ui-styling-patterns](ui-styling-patterns/SKILL.md) | 调 React 面板、侧栏的样式：嫌按钮花花绿绿、布局太松，或者要统一到全局设计变量 | 无 |
| [vite-dev-server-troubleshooting](vite-dev-server-troubleshooting/SKILL.md) | Vite 项目跑起来了，浏览器控制台却一堆报错、页面渲染坏掉，或者报错指向源码里没有的代码 | 无 |
| [run-web-project-locally](run-web-project-locally/SKILL.md) | 看到一个 GitHub 项目想"拉下来跑一下看看效果"：拉代码、装依赖、起服务，最后告诉你地址和怎么操作 | git，以及项目自己要的运行环境（多数是 Node.js） |
| [game-asset-integration](game-asset-integration/SKILL.md) | 把做好的 3D 模型、骨骼动画接进网页游戏，并且从游戏镜头里确认它真的能动、站得稳、比例对 | 无 |
| [media-processing](media-processing/SKILL.md) | 视频截图、视频转 GIF、图片改尺寸 / 裁剪 / 压缩 | ffmpeg、Python 3、`pip install pillow` |
| [image-ocr-macos](image-ocr-macos/SKILL.md) | AI 看不了图时，在 Mac 上把截图里的文字读出来（报错信息、数字表格） | macOS（用系统自带的 Swift 和文字识别，不用另装） |
| [ai-cli-batch-experiments](ai-cli-batch-experiments/SKILL.md) | 想比较不同 AI 编程工具：同一个 prompt 让 Claude Code、Codex 各跑几次，收集产物、截图、填表，只给数据不下结论 | Claude Code / Codex 命令行、Python 3、`pip install playwright` |
| [web-novel-creation](web-novel-creation/SKILL.md) | 写网文（番茄 / 起点 / 晋江）：查题材趋势、搭项目、设定世界观和人物、列章纲、写章节，或接着已有项目续写 | 无 |

## 使用前要知道

- **`ai-project-summary` 已改成目录结构。** 之前按旧说明手动建过 `ai-project-summary/` 目录的，删掉它，改成软链接仓库里的 `ai-project-summary/` 即可。
- **`mmorpg-mvp-from-scratch` 原本写给 claude.ai 用**，最后交付那步提到的 `SendUserFile` 和 Project 文档只有 claude.ai 上有。在 Claude Code、Codex 里用时，打包好的 zip 需要你按 AI 给的路径自己去拿，项目总结可以改用 `ai-project-summary` 写进仓库。
- **装了 Skill 不代表依赖也装好了。** 带脚本的 Skill（表格最后一列不是"无"的）第一次运行可能因为缺工具报错，按上表先装好。
- **各目录里的 `agents/openai.yaml` 只给 Codex 用**，决定它在界面里显示的名字和简介。用 Claude Code 可以忽略。

## 更多

- 更新记录：[CHANGELOG.md](CHANGELOG.md)
- 想新增或修改 Skill（包括让 AI 帮你维护这个仓库）：[AGENTS.md](AGENTS.md)
