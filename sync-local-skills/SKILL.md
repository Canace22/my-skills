---
name: sync-local-skills
description: 把用户在本机各个 AI agent（Claude Code、claude.ai 同步、Codex、Cursor、Hermes，以及 ~/.agents、Gemini、OpenCode、Trae 等）里自己写的 Skill 找出来，同步进这个 Skill 仓库，并按仓库约定整理、更新 README 和 CHANGELOG。当用户说「同步本地 skill」「把我在 Codex/Cursor/Hermes 里的 skill 收进来」「看看本地还有哪些 skill 没进仓库」「仓库里的 skill 和本地不一致」「备份我的 skill」时使用。
---

# 同步本地 Skill 到仓库

这个仓库是公开的。同步的目标是：把**用户自己写的** Skill 收进来，不收各 agent 自带或从商店装的，也不把个人信息、密钥带进去。

脚本只负责找和拷，判断和整理靠你。`<skill-dir>` 指本文件所在目录，脚本默认把它上两级（也就是这个仓库）当目标仓库；如果这个 Skill 是复制安装而不是软链接的，加 `--repo /path/to/my-skills`。

## 1. 扫描

```bash
python3 <skill-dir>/scripts/sync_skills.py scan
```

输出分三组：

- **NEW**：仓库里还没有的。
- **CHANGED**：仓库里有，但某个本地副本内容不同。同步过的会标「上次同步后本地又改过」，没同步记录的标副本比仓库新还是旧。
- **IN SYNC**：内容一致、本地是软链接到这个仓库的，或者本地副本自上次同步后没再改过（仓库里整理过也算）。

每个 Skill 下面的 `[A]` `[B]` 是内容不同的副本，同一行列出内容相同的所有位置。

脚本已经自动跳过：Codex 的 `.system`、Cursor 的 `skills-cursor`、claude.ai 官方 Skill（只收 `source` 为 `plugin` 的，也就是用户自己上传的）、Hermes 自带和从 Hub 装的。带 LICENSE 文件或 frontmatter 里写了 `license` 的默认藏起来，只在最后列名字，多半是从别处装的。加 `--all` 可以全部显示。

最后的 BROKEN LINKS 是指向已不存在目录的软链接，告诉用户，问 Skill 挪到哪去了。

用户的 Skill 放在别处（比如某个项目的 `.claude/skills`）时，加 `--source 名字=路径`，可以重复。

## 2. 让用户挑

把 NEW 和 CHANGED 整理成一张简短的表给用户看：名字、一句话用途、在哪个 agent、几个版本。被藏起来的那些用一行提一下名字。然后**问用户要同步哪些**，不要默认全收。

挑的时候帮用户留意这些，在表里标出来：

- **看起来不是自己写的**：作者是别人、内容是某个开源项目的通用说明、和官方 Skill 同名。
- **工作内部的**：提到公司内部系统、内部项目名、内网地址、同事名字。公开仓库不适合放，除非用户确认。
- **只对某个 agent 有意义的**：比如只讲 Hermes 自身运维的。可以收，但提醒用户别的 agent 用不上。

## 3. 拷进仓库

有多个不同版本时，先比一下再决定用哪个：

```bash
python3 <skill-dir>/scripts/sync_skills.py diff <name> --from <agent或路径>
```

拷贝：

```bash
python3 <skill-dir>/scripts/sync_skills.py import <name> [<name> ...] [--from <agent或路径>]
```

- 本地有多个不同版本而没写 `--from`，脚本会停下来列出选项。默认建议用最新的，但先跟用户确认。
- 仓库里已有的 Skill（CHANGED 组）要加 `--overwrite`。先用 `diff` 看清楚：如果仓库版本更新（比如之前已经在仓库里整理过），覆盖会把整理丢掉，这时应该反过来把差异手工合进仓库版本，或者跳过。
- 覆盖时脚本只新增和更新文件，不删仓库里多出来的文件，会把它们列出来，由你判断要不要删。
- 不确定时先加 `--dry-run` 看会动哪些文件。
- `node_modules`、`__pycache__`、`.DS_Store` 等会自动跳过。

拷完会自动跑一遍检查，并把这次用的本地副本记进 `sync-local-skills/synced.json`。之后在仓库里怎么整理，只要本地副本没再改，扫描就算已同步。这个文件要跟着提交。

两种情况用 `mark` 补记，不拷文件：

```bash
python3 <skill-dir>/scripts/sync_skills.py mark <name> [--from <agent或路径>]
```

- 把本地的改动手工合进了仓库版本。
- 用户决定不要某个本地版本（比如它比仓库旧），不想它一直出现在 CHANGED 里。

## 4. 整理成仓库的样子

逐个处理 `check` 报出的问题，改完再跑一遍直到干净：

```bash
python3 <skill-dir>/scripts/sync_skills.py check <name> [<name> ...]
```

- **frontmatter 只留 `name` 和 `description`**，`name` 和目录名一致。其他字段（`version`、`trigger`、`metadata` 等）里有用的信息挪进正文，没用的删掉。
- **写死的本机路径**（`/Users/xxx`、`~/Desktop/...`）改成相对路径、`<skill-dir>`，或者改成"用户的 XX 目录"这类说法，让 AI 运行时去问或去找。
- **疑似密钥、邮箱**：确认是真的就删掉，改成读环境变量并在正文写明变量名，然后告诉用户这个密钥曾经在本地明文存放、建议换掉。误报（比如示例占位符）可以不管。
- **运行时产生的文件**：日志、状态文件、`knowledge/xxx-log.md` 这类 agent 在使用中积累的记录、临时测试脚本（`tmp_*.mjs`、`check2.mjs` 之类），不属于 Skill 本身，删掉。拿不准的问用户。
- **脚本依赖**：看看脚本 import 了什么，非标准库的依赖要在 SKILL.md 里写清安装命令（仓库约定）。
- 正文里引用了该 agent 独有的工具或命令（比如 Hermes 的 `delegate_task`），能改成通用说法就改，改不了在 README 里注明适用的 agent。

整理时不要改写 Skill 的意思。

## 5. 更新文档

按仓库根目录 `AGENTS.md` 的约定，每个同步进来的 Skill 都要：

1. 在 `README.md` 的表格里加一行或改一行：「什么时候用」用用户的话写场景，「需要额外装什么」写清依赖，没有写"无"。
2. 在 `CHANGELOG.md` 当天日期下加一条，写明从哪个 agent 同步来。覆盖了已有 Skill、行为有变化的，标 **注意**。

写文档时用仓库里的 `human-readable-docs` Skill。

## 6. 收尾

- 给用户一份清单：同步了哪些、各自做了什么整理、哪些被跳过以及原因。
- 用户要提交时，一个 Skill 一个提交，信息用英文，比如 `sync human-writing skill from Cursor`。
- 可以提一句（不要自己动手）：把本地 agent 里的副本换成指向仓库的软链接，以后改一处各处都生效。替换前要先确认本地副本没有比仓库更新的改动，并备份原目录。
