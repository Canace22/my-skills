---
name: product-intro-video
description: >-
  Produce a short product / app feature introduction video from a feature
  description plus a few screenshots. Generates a timed narration script, a
  shot-by-shot storyboard, and a screenshot capture checklist; composites the
  user's screenshots into clean device mockups (browser / laptop / phone); and
  builds a ready-to-record slide deck (.pptx) with subtitles and transitions.
  Use this skill whenever the user wants to make a product intro video, feature
  demo, walkthrough, promo, launch/announcement video, "screen-recording +
  narration" piece, explainer, or app 功能介绍/演示/宣传视频 — even if they only
  say "介绍一下这个功能" or "帮我做个视频" without naming the format. Also trigger
  when the user has screenshots/recordings and wants them turned into a polished
  feature showcase.
---

# Product Intro Video

Turn a feature + a handful of screenshots into a recordable short video. The
skill can't literally film or screen-record — that last click stays with the
human — but it automates everything up to it: the words, the shot plan, the
mocked-up visuals, and a deck you press "record" on.

**Always produce user-facing deliverables (script, subtitles, slide text) in
the user's own language.** The instructions below are in English; the output is
not.

## What "done" looks like

Three artifacts, delivered together:

1. **Script + storyboard + shot list** — one markdown doc. The narration is
   timed to the target length, and the shot list tells the user exactly what to
   capture. This alone is useful even before any screenshots exist.
2. **Mocked-up visuals** — the user's raw screenshots composited into device
   frames so they look intentional, not like loose PNGs.
3. **A recordable .pptx** — the storyboard as slides, each with the mockup,
   on-screen subtitle, and a transition, so the user records straight through.

Deliver #1 first; it unblocks the user (they can start capturing) while you
build #2 and #3.

## Workflow

### 1. Gather what you need (ask, don't guess)

Before writing, pin down the few things that actually change the output. Ask
only what's missing from the conversation:

- **Feature** — what it is and the single most important user benefit.
- **Audience** — end users, prospects, or internal? Sets vocabulary and how
  much you explain.
- **Length** — default 90–120s. Anything past ~3 min needs a different
  structure; flag it.
- **Tone / angle** — reassuring, efficiency, "look how powerful," playful.
- **Screenshots** — does the user have them, or do they need the shot list
  first? If they have them, get the file paths.

Keep this to one focused round of questions, not an interrogation. If the user
is clearly in a hurry ("just do it"), pick sensible defaults and say what you
assumed.

### 2. Write the script + storyboard + shot list

Read `references/script-template.md` and follow its structure. The core ideas:

- **Hook first.** Open on the pain the feature removes, not on the feature.
  Users care about their problem before your solution.
- **One idea per shot.** Each scene earns its seconds by making a single point.
- **Time the narration.** Budget spoken words to the target length so it
  actually fits — the template has the rate to use per language.
- **Benefit language, never internals.** "Won't silently overwrite your work,"
  not "uses content hashing." If you know the feature's history, don't narrate
  behavior that was removed or fixed away.
- **The shot list is a promise to the user.** Number each shot, name the file
  they should save, and say whether it's a still or a recording. This is what
  lets them hand you clean material.

Save as `<feature>_intro_script.md` in the user's folder and present it.

### 3. Composite screenshots into device mockups

When the user provides screenshots, run `scripts/device_mockup.py` to drop each
into a frame instead of showing bare PNGs. This single step is what makes the
result look designed.

```bash
pip install pillow   # first time only
python scripts/device_mockup.py --input shot.png --frame laptop --output shot_laptop.png
```

Frames: `browser` (macOS-style window with traffic-light dots), `laptop`
(screen + base), `phone` (rounded slab with notch). Pick the frame that matches
where the feature lives — a desktop app reads well in `laptop` or `browser`, a
mobile feature in `phone`. See the script's `--help` for background color,
padding, and scale options.

Tip for the classic "multi-device" opening shot: render the same screenshot in
two different frames and place them side by side — this replaces filming two
real devices.

### 4. Build the recordable deck

Read `references/pptx-build.md`, then use the **pptx** skill to assemble the
slides: one slide per storyboard shot, each carrying the mockup image, the
subtitle line, and a transition. The deck is sized 1920×1080 so a screen
recording of it is clean 1080p.

### 5. Deliver

Present the script doc, the mockup images, and the .pptx together. Tell the
user the one remaining manual step: record the deck (or their live app) into a
video, optionally adding voiceover from the script. Offer to help pick a
screen-recording tool if they ask.

## Guardrails

- **Don't overstate the feature.** If you have real knowledge that a behavior
  was buggy or removed, keep it out of the narration — the video is marketing,
  and claiming a fixed-away bug as a feature backfires.
- **Respect privacy.** Remind the user to use de-identified demo data in
  screenshots; never invent real-looking personal content.
- **Length honesty.** If the requested content can't fit the requested time,
  say so and propose either trimming scope or extending the runtime.
