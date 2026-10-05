# Script + Storyboard Template

Use this structure for the deliverable doc. Adapt scene count to the target
length; the shape (hook → feature → proof → close) stays constant.

## Timing the narration

Budget spoken words so the voiceover actually fits the runtime. Rough
comfortable speaking rates (leave slack for pauses and on-screen action):

| Language | Rate | 120s budget |
|---|---|---|
| Chinese | ~4 chars/sec | ~450–520 characters total |
| English | ~2.5 words/sec | ~280–320 words total |

Count the narration as you write. If it overflows, cut — narration that races
the clock reads as an infomercial.

## Standard shape (90–120s)

| Scene | Share of runtime | Job |
|---|---|---|
| Hook | ~10% | Show the pain, not the product |
| Introduce feature | ~15% | Name it; the "one-glance" value |
| Core action | ~20% | The main happy-path in action |
| Depth / the hard case | ~35% | The moment that proves it's good |
| Payoff | ~13% | The reassuring after-state |
| Close / CTA | ~7% | Logo + one line |

The "depth" scene is the largest on purpose — it's where a feature earns
belief. For a sync feature it's conflict handling; for search it's a messy
query that still nails the result; for an editor it's the fiddly edge case made
easy. Spend your seconds there.

## Per-scene format

Write every scene with these four fields — nothing more:

```
### Scene N · <name> (m:ss–m:ss)
- **Visual**: what's on screen (which mockup / recording)
- **Narration**: the spoken line
- **Subtitle**: the on-screen caption (shorter than the narration)
- **Duration**: Ns
```

## Shot list

End the doc with a numbered capture checklist. Each item:

- a **filename** to save it as (e.g. `03_panel_pending.png`),
- **still vs recording**, and
- one line on **what state to capture** (empty state, hover, the click, the
  after-state).

Prefer recordings for anything with motion (a button spinner, a status change).
Remind the user: fixed 1080p+, window not too small, de-identified demo data,
and re-shoot the depth scene a few times to get a clean take.

## Worked example (feature: cross-device sync, users, ~115s)

- **Hook**: two devices, same doc — "edit on one, changes don't line up on the
  other?"
- **Introduce**: the little sync badge in the corner — status at a glance.
- **Core action**: open the panel, one click to push/pull, both sides match.
- **Depth**: both sides edited the same record — side-by-side local vs cloud,
  pick per field, merge & upload. Nothing gets silently overwritten.
- **Payoff**: badge back to "synced," switch devices, identical content.
- **Close**: logo + "open it and just write."
