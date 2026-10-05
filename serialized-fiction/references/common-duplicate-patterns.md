# Common Duplicate Patterns in Serialized Fiction

> Phrases and sentences that naturally recur across chapters, triggering platform duplicate detection. Identified through batch chapter writing sessions (2026-06-17).

## Why This Matters

番茄小说/起点 platform duplicate detection flags sentences that appear in multiple published chapters. AI-generated serialized fiction is especially prone to these patterns because the model reuses familiar phrasing across similar scenes.

## High-Risk Duplicate Categories

### 1. Setting Descriptions

These are the most common duplicates because the model defaults to the same atmospheric phrases:

| Pattern | Example | Fix |
|---|---|---|
| 残魂/灵力状态描写 | "残魂深处，镇魂印的暗红色光芒微微闪烁" | Change: "暗红色光晕轻轻跳动" / "暗红色符文缓缓流转" |
| 环境光线 | "阳光从树叶的缝隙中洒下来，在地上投下斑驳的光影" | Change time of day, weather, or sensory focus |
| 山洞/住所描写 | "山洞不大，只能容一个人躺下" | Vary: "岩洞很深" / "石室仅容二人" |
| 风的描写 | "风吹过他的脸，带着竹叶的清香" | Change: "山间的风带着凉意" / use听觉 instead of 触觉 |

### 2. Action Sequences

Repeated action phrases from similar scenes:

| Pattern | Example | Fix |
|---|---|---|
| 购买动作 | "谢沉走进去，买了几斤干粮和一壶水" | Vary the items, the shop type, or the interaction |
| 盘膝修炼 | "谢沉盘膝坐在山洞里，闭上眼睛" | Change: "靠在石壁上" / "在溪边坐下" |
| 感知扫描 | "他闭上眼睛，用残魂感知扫了一圈" | Change: "凝神感知四周" / "神识外放探查" |
| 角色沉默 | "谢沉沉默了" / "陆衡沉默了" | Vary: "没有立刻回答" / "顿了顿" |

### 3. Dialogue Patterns

Repeated dialogue structures across chapters:

| Pattern | Example | Fix |
|---|---|---|
| 散修警告 | "最近山里不太平，你小心点" | Change the warning content or delivery |
| 身份询问 | "你是散修？" | Vary the question or context |
| 保重祝福 | "你要保重" / "一路小心" | Use different farewell phrases |
| 厉渊对话开头 | "师父。"厉渊的声音传来 | Vary the opening or merge into narrative |

### 4. Emotional Reactions

The most insidious duplicates — they appear "natural" in every chapter:

| Pattern | Example | Fix |
|---|---|---|
| 复杂眼神 | "看着他，眼神里带着复杂的情绪" | "目光落在他脸上" / "沉默了几息" |
| 嘴唇动作 | "嘴唇动了动" | "欲言又止" / "张了张嘴" |
| 眼眶红 | "眼眶红了" | "鼻尖一酸" / "别过头去" |

### 5. Chapter Ending Patterns

AI tends to generate structurally similar endings:

| Pattern | Example | Fix |
|---|---|---|
| 镇魂印内厉渊 | "镇魂印深处，那团雾动了一下。像是在点头。" | Change the metaphor or ending focus |
| 远景收尾 | "远处的山，笼罩在晨光中" | Change time, location, or sensory focus |
| 主题句重复 | "因为活着，比什么都重要" | Each chapter needs a unique thematic statement |

## Prevention Strategy

1. **Read the previous chapter's last 300 characters** before writing the new chapter's ending
2. **Vary sensory focus**: 视觉→听觉→触觉→嗅觉 across chapters
3. **Vary time of day**: 黎明→黄昏→深夜→午后
4. **Vary location**: 室内→室外→山洞→溪边→镇上
5. **Use the duplicate check script** after every patch expansion, not just at the end

## Detection Script (Cron Mode)

```bash
python3 << 'PYEOF'
import re

def extract_sentences(text):
    sents = []
    for line in text.split('\n'):
        if line.strip() and not line.startswith('#') and not line.startswith('>'):
            for s in re.split(r'[。！？]', line):
                s = s.strip()
                if len(s) > 10: sents.append(s)
    return sents

# Read files
with open('/path/to/prev_chapter.md', 'r') as f:
    prev = f.read()
with open('/path/to/new_chapter.md', 'r') as f:
    curr = f.read()

# Inter-chapter check
prev_set = set(extract_sentences(prev))
curr_sents = extract_sentences(curr)
dupes = [s for s in curr_sents if s in prev_set]
print(f'Inter-chapter duplicates: {len(dupes)}')
for d in dupes[:5]:
    print(f'  - {d[:50]}...')

# Intra-chapter check
seen = {}
intra_dupes = []
for i, s in enumerate(curr_sents):
    if s in seen:
        intra_dupes.append((i, s, seen[s]))
    else:
        seen[s] = i
print(f'Intra-chapter duplicates: {len(intra_dupes)}')
for idx, s, first in intra_dupes[:3]:
    print(f'  - Sent {idx}: "{s[:40]}..." (first at {first})')
PYEOF
```

## Real-World Example (2026-06-17 Session)

In a 3-chapter batch write for 沉渊重生 (chapters 82-84), the following duplicates were detected and fixed:

**Chapter 82 → 83 duplicates:**
- "苏婉看着他，嘴唇动了动" → Changed to "苏婉的脸色变了"
- "他闭上眼睛，用残魂感知扫了一圈" → Changed to "他凝神感知四周"
- "沈墨的三十二个修士还在竹林里" → Changed to "竹林里，三十二道阴冷的气息仍在盘踞"
- "风吹过他的脸，带着竹叶的清香" (intra-chapter) → Changed to "山间的风带着凉意，吹动他的衣袍"
- "苍白，消瘦，指尖微微发抖" (intra-chapter) → Changed to "骨节分明，指腹带着薄茧"

**Chapter 83 → 84 duplicates:**
- "很凶，见人就问'有没有见过一个残魂修士'" → Changed to "凶得很，逢人就盘问'见过残魂修士没有'"
- "你知道他们往哪个方向去了吗？" → Changed to "他们去了哪个方向？"
- "残魂深处，镇魂印的暗红色光芒微微闪烁" → Changed to "残魂深处，镇魂印的暗红色光晕轻轻跳动"
- "但我知道一件事——你不是以前的那个谢沉了" → Changed to "我说不准。但有一点我能肯定——你跟从前判若两人"
