---
name: web-novel-creation
description: "End-to-end workflow for Chinese web novels (番茄小说/起点/晋江): trend research, project scaffolding, world-building, character design, chapter outlines, chapter writing with separate metadata files, and continuing an existing project. Use when the user wants to start, scaffold, research, outline, or continue a web novel (网文) project, or says 「写网文」「开新书」「续写」「继续更新」."
---

# Web Novel Creation (网文创作)

End-to-end workflow for creating Chinese web novels targeting platforms like 番茄小说 (Tomato Novel), 起点中文网 (Qidian), 晋江文学城 (JJWXC).

## Phase 1: Trend Research (题材搜集)

### Data Sources
1. **番茄小说 official API** — category list:
   ```
   curl -s 'https://fanqienovel.com/api/author/book/category_list/v0/' -H 'User-Agent: Mozilla/5.0'
   ```
   Returns JSON with all categories (主分类/主题/角色/情节), each with `category_id`, `name`, `description`.
   - 36 main categories (主分类): 都市脑洞, 传统玄幻, 悬疑脑洞, 豪门总裁, 种田, 快穿, etc.
   - 100+ sub-tags for themes, characters, plot elements

2. **番茄小说 hot list page**: `https://fanqienovel.com/library/male?sort=hot` / `female?sort=hot`
   - ⚠️ **PITFALL**: The rendered HTML has severe encoding issues — Chinese characters appear garbled. Use the API or browser snapshot to get partial data, but don't rely on scraping the page text directly.
   - Use browser to observe trending book titles, tags, and descriptions from the partially visible text.

3. **Cross-platform reference**: Search 起点/晋江/知乎 for genre trends via Bing (Google and Baidu block automated searches with CAPTCHA).

### Analysis Framework
For each trending genre, evaluate:
- **热度**: How many books on hot list? Search volume?
- **竞争**: Saturated or open? (玄幻/修仙 = very saturated; 都市神豪 = moderate)
- **爽点密度**: Can you pack satisfying moments every 2-3 chapters?
- **差异化空间**: Can you add a unique twist? (e.g., "restricted spending rules" for a 神豪 novel)
- **新人友好度**: Complex world-building needed? (simple = better for new writers)

### Current Trends (as of 2026-05)
- 游戏入侵 (Game Invasion) — hottest male-oriented genre
- 末世/废土穿越 — survival + ability systems
- 都市神豪/基建 — system + face-slapping + infrastructure building
- 豪门言情 — classic female-oriented, rich family drama
- 修仙苟王 — light-hearted cultivation, not hardcore

## Phase 2: Project Scaffolding

### Directory Structure
```
项目名/
├── README.md           # Title, one-line pitch, tags, platform, constraints
├── meta/project.yaml   # Metadata (genre, status, wordcount targets, tags)
├── canon/              # Read-only source facts
│   ├── 世界观.md       # World rules, power system, setting
│   └── 人物-主角.md    # Protagonist profile, backstory, arc
├── fanon/              # Story-specific additions
│   ├── 故事大纲.md     # Multi-volume outline
│   └── 关系进度.md     # Character relationship arcs
├── outline/            # Chapter-level outlines
│   └── 卷1-章纲.md     # Per-chapter synopsis
├── chapters/           # Chapter drafts
│   └── 第001章-标题.md # With metadata footer
└── notes/              # Writing notes, research
```

### README.md Template
Must include: title, one-line pitch, tags, target platform, writing constraints (word count, hook rules, paragraph length), and **differentiation pitch** — what makes this novel different from the 100 others in the same genre.

### project.yaml Fields
```yaml
title: 书名
author: 待定
genre: 分类
platform: 番茄小说
status: 连载中/筹备中
target_wordcount: 2000000
chapter_wordcount: 1200-1800
update_frequency: 日更2章
tags: [tag1, tag2]
synopsis: 一句话简介
created: YYYY-MM-DD
version: 0.1.0
```

## Phase 3: World-Building & Characters

### World Rules (世界观.md)
- Setting (time, place, tone)
- Power/ability system (if any) — define rules, limits, progression clearly
- Social environment relevant to the plot
- Keep it concise — readers don't need a 10-page wiki, they need enough to write consistently

### Character Profiles (人物-主角.md)
- Basic info (name, age, appearance)
- Pre-story backstory (what shaped them)
- Personality traits (3-5 specific, with examples)
- Character arc (beginning → middle → end transformation)
- Speech patterns / habits (makes dialogue distinct)
- Initial relationship map

## Phase 4: Outline

### Story Outline (故事大纲.md)
- Use 3-volume or 5-volume structure
- Each volume: core theme, key events (with chapter ranges), climax
- Include: romance arc progression, villain arc, escalation pattern
- **爽点节奏**: Map satisfying moments — small ones every 2-3 chapters, big ones every ~10 chapters

### Chapter Outline (章纲.md)
Per chapter include:
- Chapter number and title
- Word count target
- Core event
- Opening hook (first 100 chars must grab attention)
- Key dialogue snippets
- Chapter-ending cliffhanger
- 爽点 (satisfaction point)
- 伏笔 (foreshadowing)

## Phase 5: Chapter Writing

### Hard Rules (番茄小说 style)
1. **Word count**: 1200-1800 per chapter
2. **Opening hook**: Something must happen in the first 300 characters
3. **Chapter ending**: Must have a cliffhanger or悬念
4. **Paragraphs**: 2-3 lines max
5. **Dialogue**: Interleave with action beats — never pure dialogue blocks
6. **Pacing**: Fast. No long internal monologues, no info-dumps
7. **Metadata footer**: Every chapter ends with a metadata block (word count, core event, 爽点, 钩子, 伏笔)

### Chapter Template

Chapter files contain ONLY the prose. Metadata lives in a separate file.

**第X章-标题.md** (chapter content only):
```markdown
# 第X章：标题

[正文 1200-1800字]
```

**第X章-元数据.md** (separate metadata file):
```markdown
# 第X章 · 元数据

> 与 `第X章-标题.md` 配对
> 最后更新：YYYY-MM-DD

## 基本信息

| 项 | 内容 |
|---|---|
| 章节号 | 第X章 |
| 字数 | 约XXXX字 |
| 核心事件 | xxx |

## 叙事记录

| 项 | 内容 |
|---|---|
| 主推进 | xxx |
| 主冲突 | xxx |
| 节奏位置 | xxx |
| 章尾钩子 | xxx |
| 爽点 | xxx |

## 伏笔
- xxx

## 备注
- xxx
```

### Metadata File Rules

1. **Naming**: `第NNN章-元数据.md` (zero-padded 3 digits)
2. **Location**: Same `chapters/` directory as the chapter file
3. **NEVER put metadata at the bottom of chapter content** — users copy-paste chapter text and metadata gets mixed in
4. **Metadata is optional for simple projects** — only generate when user requests or project has complex continuity needs

## Continuation Workflow (续写/继续更新)

When the user says "继续更新", "继续写", "续写", or similar — they want to continue an **existing** project, not create a new one. Follow this workflow:

### Step 0: Project Discovery
1. **Check for project-local AGENTS.md** — if the project directory has `AGENTS.md`, read it first. It defines project-specific skills, required read order, and working rules that override this skill.
2. **Check for project-local skills** — many repos have `skills/` directory with their own `SKILL.md` files (e.g., `fanfic-bible-skill`, `chapter-writer-skill`, `narrative-rhythm-skill`). Load these as the project's AGENTS.md instructs, not as global skills.

### Step 1: Read Progress
Read these in one batch rather than one call per file:
```bash
# Read project progress
cat "$PROJECT/meta/project.yaml"

# List existing chapters (also reveals the numbering format in use)
ls "$PROJECT/chapters/" | grep -v 元数据

# Read the last 2 chapters' metadata for context
cat "$PROJECT/chapters/第${PREV}章-元数据.md" "$PROJECT/chapters/第${LAST}章-元数据.md"
```

### Step 2: Determine What's Next
- If `current_chapter` matches the last chapter in the volume outline → **volume transition**
- If detailed chapter outlines (章纲) exist for the next chapters → **write directly**
- If only a volume outline (大纲) exists → **create detailed chapter outlines first**, then write

### Step 3: Batch Write (3 chapters recommended)
Efficient batch pattern:
1. Create detailed chapter outlines (if needed) → `outline/卷N-章纲.md`
2. Write all chapter prose → `chapters/第NN章.md`
3. Write all metadata → `chapters/第NN章-元数据.md`
4. Sync fanon once (new characters, relationships, world-building)
5. Update `meta/project.yaml` and `README.md` once

**PITFALL**: Don't write chapter prose, then metadata, then fanon for each chapter individually. This wastes tool calls. Batch all prose → batch all metadata → sync fanon once → update project files once.

### Step 4: Volume Transition
When a volume ends:
1. Add `# 卷N《卷名》完` at the end of the last chapter
2. Create `outline/卷(N+1)-大纲.md` if not exists
3. Create `outline/卷(N+1)-章纲.md` for at least the first 3-4 chapters
4. Update `project.yaml` to new volume number

### Step 5: Fanon Sync Checklist
After writing chapters, always update:
- `fanon/新人物.md` — new characters introduced this batch
- `fanon/关系进度.md` — relationship changes
- `fanon/世界观补丁.md` — new world-building details (if applicable)
- `meta/project.yaml` — `current_volume` and `current_chapter`
- `README.md` — progress table

## Pitfalls

- **NEVER put metadata at the bottom of chapter files** — users copy-paste chapter text for publishing and metadata gets mixed in. Use separate `第NNN章-元数据.md` files instead. This was a user correction (2026-05-29).

- **Don't scrape fanqienovel.com HTML directly** — encoding is broken. Use the API endpoint.
- **Google and Baidu block automated searches** — use Bing or DuckDuckGo for trend research.
- **Chinese-language queries return no results via web_search** — the search tool handles English queries well but Chinese text (e.g. "番茄小说 热门榜") returns nothing. Workaround: use English queries (e.g. "Chinese web novel trends 2026") + Reddit r/noveltranslations, or delegate to a subagent that can try multiple query variations. Cross-platform comparison (起点/晋江) requires English queries or relying on training knowledge.
- **Don't over-design the world** before writing — start simple, expand as needed.
- **Don't write too many chapters upfront** — write 3 sample chapters, confirm direction with user, then continue.
- **Don't change chapter numbering format** — if the project uses `第01章`, keep using 2-digit zero-padding. If it uses `第1章`, don't add padding. Check existing files with `ls chapters/` before writing.
- **Don't write metadata at the bottom of chapter files** — users copy-paste chapter text for publishing and metadata gets mixed in. Use separate `第NN章-元数据.md` files instead.
- **Check project-local AGENTS.md before writing** — many projects have their own skills, read order, and constraints (e.g., `fanfic-bible-skill`, `narrative-rhythm-skill`). These override the global skill. Look for `AGENTS.md` in the project root, and `skills/` directory for project-specific skills.
- **Always check session_search before continuing** — find out what was already written, what corrections were made, and what conventions were established. Starting blind wastes the user's time.
- **Differentiation matters** — don't just copy trending genres. Add a unique twist (e.g., restricted spending rules for 神豪, specific game mechanics for 游戏入侵).
- **爽点 must feel earned** — not just "MC is rich and everyone is shocked." Build up the situation, then deliver the payoff.
