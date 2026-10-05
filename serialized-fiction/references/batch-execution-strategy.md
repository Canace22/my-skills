# Batch Chapter Execution Strategy

> Writing 2+ chapters per session (especially across multiple projects) requires careful planning to avoid hitting iteration limits and to maintain quality.

## Iteration Budget

Each chapter consumes approximately **8-12 tool calls** in the full auto-pipeline:

| Step | Tool Calls | Notes |
|---|---|---|
| Read context | 2-3 | Can batch reads in one terminal call |
| Title dedup check | 1 | grep command |
| Write chapter | 1 | Initial draft via write_file |
| Word count check | 1 | Python heredoc |
| Duplicate check | 1 | Python heredoc |
| Patch expansions | 1-4 | Each patch needs word count recheck |
| Write metadata | 1 | write_file |
| Update fanon files | 1-2 | cat heredoc per file |
| Update README + yaml | 1-2 | sed commands |

**Realistic budget**: 10-15 tool calls per chapter, 20-30 if expansions needed.

**For ~50 tool call limit:**
- 3 chapters = 30-45 calls (doable)
- 6 chapters = 60-90 calls (will hit limit)
- 6 chapters across 2 projects = 70-100 calls (very likely to hit limit)

## Multi-Project Execution Order

1. **Complete one project fully before starting the next.** Context switching wastes tool calls on re-reading.
2. **Read all context upfront** in one batch terminal call.
3. **If hitting limits**, write all prose first, then batch metadata/fanon/README updates.
4. **Mark incomplete chapters clearly** in the final report.

## Chapter Ending Repetition Trap

AI tends to produce similar reflective endings across consecutive chapters:
- "窗外的海面/江城在夕阳下泛着金色的光"
- "远处的高楼大厦/渔船在天际线上排列着"

**Prevention**: Before writing each ending, check what the previous chapter ended with. Vary time of day, location, tone, and sensory focus.

## 实测数据（2026-06-15）

6 章跨 2 个项目（沉渊重生 3 章 + 神豪降临 3 章）的批量写作：

| 章节 | 初稿字数 | 扩充轮次 | 最终字数 | 总工具调用 |
|---|---|---|---|---|
| 沉渊76 | 1740 | 3轮 | 2067 | ~10 |
| 沉渊77 | 1983 | 2轮 | 2010 | ~8 |
| 沉渊78 | 2229 | 0轮 | 2229 | ~7 |
| 神豪55 | 1928 | 3轮 | 2003 | ~10 |
| 神豪56 | 1777 | 3轮 | 1968 | ~10 |
| **总计** | | | | **~45** |

**结论**：5 章消耗约 45 次工具调用，第 6 章未能完成（达到迭代上限）。如果目标是每 cron job 写 6 章，需要：
- 减少扩充轮次（初稿瞄准 140%）
- 批量读取上下文（合并多个 `cat` 为一次 `terminal` 调用）
- 合并 duplicate fix + expansion 到同一轮 patch
- 或者将 6 章拆成两个 cron job
