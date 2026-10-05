# 维护约定

给维护这个仓库的人和 AI 看。用户怎么用看 [README.md](README.md)。

## 仓库结构

每个 Skill 一个目录，目录名就是 Skill 名（小写短横线）：

```text
<skill-name>/
├── SKILL.md            # 必需：frontmatter + 给 AI 的操作说明
├── scripts/            # 可选：SKILL.md 里调用的脚本
└── agents/openai.yaml  # 可选：Codex 界面显示名、简介、默认提示词
```

根目录只放 `README.md`、`CHANGELOG.md`、`AGENTS.md`。

## SKILL.md 写法

- frontmatter 只写 `name` 和 `description`。`name` 必须和目录名一致。
- `description` 决定 AI 什么时候触发这个 Skill：写清楚"做什么 + 用户会怎么说"，把常见说法直接列进去。
- 正文中英文都行，跟着这个 Skill 的主要使用场景走；同一个文件内不要混着写。
- 脚本路径在正文里用相对路径（`scripts/xxx.py`）或 `<skill-dir>` 占位，不要写死本机绝对路径。
- 脚本优先用标准库；必须装的依赖在 SKILL.md 里写出安装命令。

## 新增或修改一个 Skill 时

每次都要同步三处，缺一处就算没做完：

1. **Skill 本身**：目录、`SKILL.md`、脚本。
2. **README.md 的表格**：加一行或改一行。"什么时候用"一列用用户的话写场景，"需要额外装什么"写清依赖；没有就写"无"。如果这次改动会让已有用户踩坑，在「使用前要知道」里加一条消化过的提醒（说清改了什么、怎么应对）。
3. **CHANGELOG.md**：在当天日期下加一条；影响已安装用户的标 **注意**。

README 顶部永远留给第一次来的人，不要在顶部追加"本次更新"。写或改文档时用 [human-readable-docs](human-readable-docs/SKILL.md) 这个 Skill。

## 提交

- 一个 Skill 的改动一个提交，信息用英文，格式随意但要说清对象，比如 `add WPS Markdown cleanup skill`、`improve WPS heading renumbering`。
- 不要提交 `.DS_Store`（已在 `.gitignore` 里）。
