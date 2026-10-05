# Building the Recordable Deck

The deck is not the final video — it's a canvas the user screen-records into
one. Optimize for a clean 1080p capture and readable-on-playback text.

## Setup

- Slide size **1920×1080 px** (16:9). In python-pptx:
  `prs.slide_width = Inches(13.333)`, `prs.slide_height = Inches(7.5)`.
- One slide per storyboard scene, in order.
- Dark or brand-colored background so mockups and captions pop. Keep it
  consistent across slides.
- Use the **pptx** skill for the actual construction — this file only says what
  goes on each slide.

## Per-slide layout

Each slide carries three things:

1. **The visual** — the device-mockup PNG from `device_mockup.py`, centered,
   with breathing room (don't bleed to the edges).
2. **The subtitle** — the scene's on-screen caption, large (40–54pt), high
   contrast, lower third. This is the caption from the storyboard, not the full
   narration.
3. **A section tag** (optional) — a small kicker like "01 / Sync status" top
   corner, for orientation.

For the multi-device hook, place two mockups side by side on one slide.

## Motion

The user records the deck playing, so motion comes from slide **transitions**
and **builds**:

- Use a gentle transition (fade or push) between slides — python-pptx can set
  this via the slide's XML transition element.
- Advance timing: set each slide's auto-advance to roughly its storyboard
  `Duration` so a straight playthrough matches the script. In PowerPoint terms,
  that's the slide's advance-after time.
- Where a scene has a real recording (a spinner, a status flip), leave a
  placeholder slide and note that the user drops the recording in there, or
  records their live app for that beat and cuts it in.

## Handing off

Tell the user how to turn the deck into a video:

- **Record it**: play the deck full-screen and screen-record, or use
  PowerPoint/Keynote "Export as Video."
- **Voiceover**: read the narration column while recording, or record audio
  separately and lay it over.
- The script doc is the teleprompter — narration column top to bottom.
