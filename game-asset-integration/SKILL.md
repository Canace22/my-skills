---
name: game-asset-integration
description: "Wire finished 3D assets (GLB models, rigs, animations, props) into a running browser game so they actually play, not just display. Use when replacing placeholder geometry with real art, when a generated model batch needs to go into the game, or when checking whether an integrated character works from the game camera."
---

# Game Asset Integration

Getting finished 3D assets (models, rigs, animations, props) into a running game so they
actually play, not just display. Applies to browser games using three.js or similar.

## When to Use

- Dropping finished GLB characters, props, or rigs into an existing game/demo
- Replacing placeholder/procedural geometry with the real art
- A generated model batch arrives and someone asks "wire these into the game"
- Rigging/animating assets that will be consumed by a game

---

## Order the pipeline so integration happens once

**Finish the expensive asset pipeline — rig, skin, animation — BEFORE wiring the asset into
the game.** Integrating a static mesh "for now" and swapping in the rigged version later
doubles the work and hides the real risk:

- every prop/attachment offset gets calibrated twice,
- procedural stand-in animation (bob/tilt) written for the static mesh has to be deleted,
- and a static integration only proves the model *displays*, not that it *plays*.

If the generator supports rigging (e.g. Meshy `v1/rigging` + animation presets, binding a rig
to an existing model by `input_task_id` rather than re-generating), use it. Do not hand-build
an armature in Blender when the pipeline that produced the model can produce the skeleton and
animation clips itself.

Static meshes are a legitimate end state only when no rig is possible; then name the limitation
in the report instead of implying the character animates.

---

## Establish asset facts before specifying anything

Never assume a "finished" batch is rigged, uniformly scaled, or facing the expected direction.
Parse the GLB JSON chunk and read `skins`, `animations`, node count, and accessor `min`/`max`
for real dimensions. A batch that looks complete can be 100% static single-node meshes with no
walk cycle to reuse — discovering this after writing the task wastes a round.

Snippet and a reading table: `references/2.5d-asset-integration.md`.

Put the measurements into the brief as a fact table (per-asset width/height/depth, triangle
count, skins/animations present). It removes a whole class of "the executor guessed a scale"
churn.

---

## Acceptance is camera-relative, not model-relative

Never accept a free-orbit view, a standalone model-preview page, or a viewer screenshot as
evidence that integration works. The frame that matters is the one the player sees.

For a **2.5D / fixed-camera** game (3D scene, fixed oblique camera, characters moving along one
horizontal axis and facing only left/right), judge by these:

- **Silhouette legibility** — at game camera distance the character is small; whether a walk
  cycle reads is judged from the outline, not from animation data or poly count.
- **Ground contact** — floating, sunken, or hovering is obvious in a fixed camera. Check every
  state, frame by frame.
- **Scale against scene props** — the character/prop ratio is a hard picture constraint; compare
  against the real set dressing, not against a number in a spec.
- **Front/back occlusion** — characters sharing one movement axis overlap; confirm draw order
  and interpenetration on screen.
- **Left/right only** — do not tune for 360° presentation; confirm both facings read and the
  turn transition is clean.

A free-camera 3D game has looser constraints (the player can orbit), which is exactly why a
2.5D acceptance list must be written in the game's own terms rather than borrowed from 3D.

---

## Make the real asset opt-in and failure-safe

Async model loading in a single-file game needs three guards, all of which are cheap:

1. **A feature constant** (`FORMAL_AVAILABLE = false` until the asset actually exists) so the
   normal path never requests a missing file and never logs a 404.
2. **Graceful degradation** on load failure, `file://`, or 404 — fall back to the existing
   placeholder so the game stays playable. GLB has the same `file://` restriction as sprite
   images, so the game must be served over HTTP.
3. **A URL flag** (e.g. `?legacy-characters`) forcing the placeholder, for side-by-side
   comparison and for isolating "is this the asset, or the integration?".

Keep the fallback path alive rather than deleting it — the placeholder *is* the rollback.

---

## Attachment points follow the character

Props modelled with the origin at the grip centre attach with scale + offset only — no
re-modelling.

- Attach to the character's hand **bone**, not to a hand-rolled limb cylinder. A bone-parented
  prop follows the animation for free; a cylinder-parented one drifts as soon as the rig moves.
- **Re-calibrate every offset whenever the character model changes**, including a
  placeholder→formal swap. Offsets tuned against the placeholder are wrong against the real mesh.
- Keep all offsets in one explicit config table so the next swap is a data edit, not a code hunt.

---

## Pitfalls

1. **Don't integrate a static asset to "see it in game" while a rig is still pending** — the
   calibration and stand-in animation get thrown away, and the preview proves nothing about play.
2. **Don't trust the label.** A file named `*-walk-*.glb`, or a source model with a promising
   name, may have zero animations. Read `skins`/`animations` from the GLB before planning around it.
3. **Model bottoms at `min[1] ≈ 0`** means the asset was authored standing on the origin; any
   other value floats or sinks unless you offset it at attach time.
4. **Facing direction is almost never what you assume** from the export axes. Confirm it from a
   render, then record `rotationY` in the config table.
5. **A model can contradict its own written setting** (e.g. a character specified as half human
   height modelled at full human height). Do not edit the asset — scale it in the game and log the
   asset as needing revision.
6. **Re-verify every claim yourself.** Take the size, orientation, and animation claims from the
   executor's report and check the files and screenshots directly before telling the user it works.

---

## References

- `references/2.5d-asset-integration.md` — GLB inspection snippet, size-normalisation notes, and
  the full integration acceptance checklist.
