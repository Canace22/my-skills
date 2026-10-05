# Batch Chapter Writing Workflow

> Reference for writing multiple chapters across multiple novels in a single session (e.g., cron job).

## Workflow Diagram

```
1. Check Status (all novels)
   ├── Read meta/project.yaml for each
   ├── Find current_chapter and next_action
   └── Detect blockers (missing outlines, completed volumes)

2. Load Context (per novel)
   ├── Read canon/*.md for characters in this batch
   ├── Read fanon/关系进度.md
   ├── Read last 2 chapter metadata files
   ├── Read outline for target chapters
   └── Read forbidden words list (if exists)

3. Write Chapters (per novel, sequential)
   ├── Confirm chapter contract (四件套)
   ├── Write prose (check project README for word count target, default 2000-4000)
   ├── Write metadata file
   └── Sync fanon files

4. Update Project Files (per novel)
   ├── Update meta/project.yaml (current_chapter, next_action)
   ├── Update README.md (progress table)
   └── Update fanon/关系进度.md (timestamp)

5. Quality Check (per novel)
   ├── Run forbidden words grep
   ├── Verify chapter count matches plan
   └── Verify word count in target range

6. Generate Summary
   ├── List chapters written per novel
   ├── Include chapter titles
   └── Include total word counts
```

## Status Check Pattern

```python
import os

def check_novel_status(project_path):
    """Check current state of a novel project."""
    yaml_path = os.path.join(project_path, "meta", "project.yaml")
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    # Parse key fields
    current_chapter = None
    next_action = None
    for line in content.split('\n'):
        if 'current_chapter:' in line:
            current_chapter = int(line.split(':')[1].strip())
        if 'next_action:' in line:
            next_action = line.split(':', 1)[1].strip()
    
    # Check if volume outline exists
    # (infer from current_chapter and outline files)
    outline_path = os.path.join(project_path, "outline")
    outlines = os.listdir(outline_path) if os.path.exists(outline_path) else []
    
    return {
        'current_chapter': current_chapter,
        'next_action': next_action,
        'outlines': outlines
    }
```

## Batch Context Loading

```python
def load_batch_context(project_path, chapter_numbers):
    """Load context for multiple chapters at once."""
    context = {}
    
    # Load canon files
    canon_path = os.path.join(project_path, "canon")
    if os.path.exists(canon_path):
        for f in os.listdir(canon_path):
            with open(os.path.join(canon_path, f), 'r') as fh:
                context[f"canon/{f}"] = fh.read()
    
    # Load fanon files
    fanon_path = os.path.join(project_path, "fanon")
    if os.path.exists(fanon_path):
        for f in os.listdir(fanon_path):
            with open(os.path.join(fanon_path, f), 'r') as fh:
                context[f"fanon/{f}"] = fh.read()
    
    # Load recent chapter metadata
    chapters_path = os.path.join(project_path, "chapters")
    for ch_num in chapter_numbers:
        meta_file = f"第{ch_num:02d}章-元数据.md"
        meta_path = os.path.join(chapters_path, meta_file)
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as fh:
                context[f"meta/{meta_file}"] = fh.read()
    
    return context
```

## Forbidden Words Check

```python
import re

def check_forbidden_words(chapters_path, forbidden_words_file, new_chapters):
    """Check new chapters for forbidden words."""
    # Load forbidden words
    with open(forbidden_words_file, 'r') as f:
        content = f.read()
    
    # Extract words from table (simple regex)
    forbidden = []
    for line in content.split('\n'):
        if '|' in line and '原作专属' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if parts and parts[0]:
                # Split multiple words by /
                words = [w.strip() for w in parts[0].split('/')]
                forbidden.extend(words)
    
    # Check each chapter
    results = {}
    for ch_file in new_chapters:
        ch_path = os.path.join(chapters_path, ch_file)
        if os.path.exists(ch_path):
            with open(ch_path, 'r') as f:
                text = f.read()
            found = [w for w in forbidden if w in text]
            results[ch_file] = found if found else "无禁词"
    
    return results
```

## Word Count Verification

```python
def count_chinese_chars(text):
    """Count actual Chinese characters in text. Use this for metadata."""
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')

def generate_word_count_summary(project_path, chapter_files):
    """Generate word count summary for a batch of chapters."""
    total = 0
    chapters = []
    
    for ch_file in chapter_files:
        ch_path = os.path.join(project_path, "chapters", ch_file)
        if os.path.exists(ch_path):
            with open(ch_path, 'r') as f:
                content = f.read()
            chars = count_chinese_chars(content)
            total += chars
            chapters.append((ch_file, chars))
    
    return chapters, total
```

## Common Pitfalls

0. **Outline-to-actual chapter remapping**: When chapters get merged or split vs. the outline (e.g., outline ch47-49 merged into actual ch47), the chapter numbering diverges. Before writing a batch: (1) read the last 2-3 actual chapter metadata to understand what outline content has already been covered, (2) map remaining outline chapters to the next actual chapters, (3) record the mapping in the batch context so each subsequent write knows which outline beats to hit. A common mistake is writing outline ch48 content when actual ch47 already covered it — this causes duplicated events and wasted chapters.

1. **Stale next_action**: Always verify `next_action` matches reality. If it says "开卷纲" but you're mid-volume, fix it.

2. **Missing volume outline**: If `next_action` says "需开卷纲", create the outline FIRST. Don't try to write chapters without it.

3. **Forbidden words check timing**: Run the check AFTER writing ALL chapters for a novel, not after each chapter. This is more efficient.

4. **Project file updates**: Don't wait until all novels are done. Update each novel's files after finishing its chapters.

5. **Word count target**: Always read the project `README.md` for `单章字数` before writing. Do NOT rely on skill defaults or memory — the project file is the source of truth. If the cron job prompt has a hardcoded word count that differs from the project README, the README wins (and the cron prompt should be updated).

6. **Subagent delegation failure**: In cron job or API-constrained contexts, `delegate_task` may fail with 401 or other errors. **Do not retry** — fall back to direct sequential writing immediately. Pattern: write chapter prose → write metadata → write next chapter → ... → update project.yaml and fanon files at the end. The sequential approach is slower but reliable.

7. **Word count in metadata must be verified, not estimated**: After writing a chapter, count actual Chinese characters (`sum(1 for c in text if '\u4e00' <= c <= '\u9fff')`) and use THAT number in the metadata file. Do not estimate from prose length or total file size. Metadata word count is a continuity bridge — wrong numbers mislead future sessions about pacing.

8. **Chapter filename numbering varies by project**: Some projects use bare numbers (`第41章.md`), others use zero-padded 3-digit (`第026章.md`), others embed the title in the filename (`第001章-重生毕业日.md`). Always check existing filenames in `chapters/` before writing new ones. The format is set by the first chapters and must be continued consistently.

9. **Batch writing across 2+ novels — context management**: When writing 3+ chapters for multiple novels in one session, load ALL context for one novel first (outlines, canon, fanon, recent chapters), write all its chapters, update its project files, then move to the next novel. Do not interleave — context window pressure causes OOC drift and continuity errors.

10. **Fanon sync checklist is mandatory per novel, not per session**: The fanon sync checklist (新人物/世界观补丁/关系进度) must be run after finishing ALL chapters of a novel, not after each individual chapter. Batch the updates to avoid redundant file reads.

11. **Intra-chapter duplicate check after patch expansion**: When expanding a chapter with `patch` to meet word count, the same thematic sentence can appear in two different sections (e.g., a reflection in the opening and a similar reflection in the closing). After each `patch` expansion, run an intra-chapter duplicate check before running the inter-chapter check. See the main SKILL.md duplicate check section for the script.

12. **Cron mode blocks `execute_code`**: In cron jobs, `execute_code` is unavailable. All code examples in this document that use `execute_code` must be adapted to use `terminal` + Python (no Chinese string literals in code) or heredoc Python scripts. See `references/cron-mode-workarounds.md` for the complete fallback mapping. Key adaptations:
    - Word counting → `terminal` + Python reading from file
    - Duplicate checks → `terminal` + Python heredoc
    - File editing with Chinese text → `patch` or `write_file` tools
    - README updates → Python tempfile pattern (see cron-mode-workarounds.md Approach 2)
    - Fanon updates → `terminal` + `cat >>` heredoc

---

## Concrete: Single Chapter Cycle in Cron Mode

This is the exact tool call sequence used successfully in a 2026-06-14 cron job writing 6 chapters across 2 novels:

### Phase 1: Read Context (per chapter)
```
1. read_file  → meta/project.yaml (get current_chapter, next_action)
2. read_file  → outline/卷N-章纲.md (get 四件套 for target chapter)
3. read_file  → chapters/第XX章-元数据.md (last chapter's state)
4. read_file  → canon/人物-*.md (characters in this chapter)
5. read_file  → fanon/关系进度.md (current relationship states)
```

### Phase 2: Title Dedup
```
6. terminal   → grep -h "^# 第" chapters/第[0-9]*章.md | grep -v 元数据 | sort | uniq -d
```

### Phase 3: Write Chapter
```
7. write_file → chapters/第XX章.md (full chapter prose, aim for 120% of target word count)
```

### Phase 4: Word Count + Duplicate Check
```
8. terminal   → python3 -c "import re; ..." (word count from file)
9. terminal   → python3 << 'PYEOF' ... PYEOF (inter-chapter duplicate check)
10. terminal  → python3 << 'PYEOF' ... PYEOF (intra-chapter duplicate check)
```

### Phase 5: Expand if Needed (loop until word count met)
```
11. terminal  → python3 << 'PYEOF' ... PYEOF (find insertion point, expand via Python file I/O)
12. terminal  → python3 -c "..." (re-count)
13. terminal  → python3 << 'PYEOF' ... PYEOF (re-check duplicates after expansion)
```

### Phase 6: Write Metadata
```
14. write_file → chapters/第XX章-元数据.md
```

### Phase 7: Sync Fanon (after ALL chapters of a novel)
```
15. terminal  → cat >> fanon/新人物.md << 'EOF' ... EOF
16. terminal  → cat >> fanon/关系进度.md << 'EOF' ... EOF
17. terminal  → python3 << 'PYEOF' ... PYEOF (append to fanon/世界观补丁.md with auto-numbering)
```

### Phase 8: Update Project Files
```
18. terminal  → python3 << 'PYEOF' ... PYEOF (README.md tempfile update)
19. terminal  → python3 << 'PYEOF' ... PYEOF (meta/project.yaml sed-like update)
20. terminal  → cat >> outline/卷N-章纲.md << 'EOF' ... EOF (append new chapter contracts)
```

### Key Observations from Real Execution
- **Word count expansion**: AI first drafts consistently come in 20-30% below target. Plan for 1-3 expansion rounds per chapter.
- **Expansion technique**: Adding dialogue exchanges is the most efficient way to add 100-200 chars per patch. Environment descriptions add fewer chars per effort.
- **Duplicate check results**: Most chapters pass cleanly. When duplicates appear, they're usually structural phrases ("他闭上眼睛"、"林远看着他") that need rewording.
- **Total time**: 6 chapters across 2 novels took ~30 tool calls. Plan accordingly for cron job timeouts.
