# Serialization Automation Workflow

> Workflow for automated daily chapter updates (cron job pattern).

## Step-by-Step Execution

### 1. Read Progress
For each project:
- Read `meta/project.yaml` → get `current_volume`, `current_chapter`
- Read the last 2 `chapters/第XX章-元数据.md` → context
- Read `fanon/故事大纲.md` → big picture
- Read `outline/卷N-章纲.md` → next chapter contract

### 2. Check Completion
- Compare `current_chapter` against the outline's total chapters
- If outline doesn't cover all chapters, check volume overview for remaining beats
- If all chapters written → mark as "完结", notify user

### 3. Write Chapters
For each chapter to write:
- Confirm the 四件套 (主推进, 主冲突, 节奏位, 章末钩子)
- Write prose following serialized-fiction Part 3 (Chapter Writing Workflow)
- Write metadata following metadata template
- Sync fanon files after each chapter

### 4. Update Supporting Files
After all chapters written:
- `fanon/关系进度.md` — relationship changes
- `fanon/世界观补丁.md` — new worldbuilding
- `fanon/新人物.md` — new characters
- `meta/project.yaml` — progress update
- `README.md` — progress table update

### 5. Notify
Produce a summary including:
- Each chapter's title, main event, end hook
- Key foreshadowing planted/advanced
- If novel completed: mark clearly, suggest canceling cron job
- If all novels completed: suggest deleting the cron job entirely

## Multi-Project Handling

When updating multiple projects:
- Alternate between projects (e.g., Project A 3 chapters, then Project B 3 chapters)
- If a project is complete, skip it
- Each project's updates are independent

## Pitfalls

- **Always check if outline covers the chapters you're writing.** If writing beyond the detailed outline, use volume overview beats.
- **Don't forget to update README.md progress table.** It's the user's quick-glance status.
- **Completion notification is critical.** If a novel finishes and no one tells the user, the cron job keeps running pointlessly.
