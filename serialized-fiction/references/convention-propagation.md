# Convention Propagation Map

> When changing a project-wide convention in a fiction repository, these are ALL the locations that may need updating.

## Convention: Word Count (字数)

| Location | Format | Example |
|---|---|---|
| `notes/章节写作规范备忘.md` | `每章字数必须在 X-Y 字之间` | Core rule |
| `projects/<项目>/README.md` | `单章字数 | X-Y 字` | Per-project setting |
| `projects/<项目>/fanon/故事大纲.md` | `- 单章 X-Y 字` | Writing constraints section |
| `projects/<项目>/outline/卷N-大纲.md` | `- 单章 X-Y 字` | Per-volume writing constraints |
| Cron job prompt (job_id varies) | `每章 X-Y 字` in the task instructions | Automated writing rules |
| `serialized-fiction` skill `SKILL.md` | Word count table in Part 2 | Skill default |

## How to Update

1. Update `notes/章节写作规范备忘.md` (repo-level rule)
2. Update each project's `README.md`
3. Update each project's `fanon/故事大纲.md` writing constraints
4. Update each volume outline's writing constraints
5. **Update the cron job prompt** via `cronjob(action='update')` — this is the most commonly missed step!
6. Verify with `cronjob(action='list')` that the prompt reflects the new rule

## Pitfall

The cron job prompt is a SNAPSHOT copied at creation time. Changing project files does NOT automatically update the cron job. You must explicitly update the cron job prompt to match.

## Convention: Writing Style / Format Rules

Same propagation pattern. The `notes/章节写作规范备忘.md` is the canonical source, but cron jobs and per-project READMEs may carry stale copies.
