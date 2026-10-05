---
name: anime-gothic-character
description: Generate exactly one full-body anime-style gothic character as a clean transparent PNG. Use for isolated gothic military, aristocratic, manga-cover, or game-character cutouts; do not use for multi-character scenes or background illustrations.
---

# Anime Gothic Character

Create one production-ready character cutout. Use the built-in image generation tool; do not substitute SVG, HTML, or a hand-drawn placeholder.

## Build the prompt

Keep user-provided appearance, costume, pose, and palette requirements exact. When details are omitted, use this baseline:

- One slim, beautiful young adult man with pale skin, delicate aristocratic features, sharp crimson eyes, tousled teal-black hair, and a dangerous, slightly seductive smile.
- An ornate black gothic military uniform with a high collar, layered leather, silver chains, fitted gloves, straps, epaulettes, metal fasteners, and a ceremonial military cap.
- Sophisticated anime line art, soft painterly cel shading, restrained halftone and ink texture, and a black-heavy palette with restrained teal, crimson, and cool-silver accents.
- One centered head-to-toe figure with the complete cap and both boots visible. Preserve a clean silhouette and readable negative spaces.

State these constraints explicitly: exactly one character, young adult, no crop, no props floating separately, no text, no watermark, no floor, no cast shadow, and no scenery.

## Produce true transparency

1. First request a genuine transparent alpha background. Say that checkerboard pixels, white or gray mattes, gradients, and glow fields are forbidden.
2. Save the selected PNG into the user's requested location or the current project's output directory.
3. Run `scripts/verify_transparency.swift <image.png>`. Do not infer transparency from a checkerboard preview or `.png` extension.
4. Visually inspect the saved image. Confirm exactly one intact figure, full-body framing, clean edges, and no background remnants.
5. If validation fails, make one background-extraction edit with the built-in image generator. Preserve the character's face, costume, pose, proportions, colors, details, and framing exactly; replace only the background with actual alpha. Validate the saved file again because an edit can still return an RGB image with a baked checkerboard.
6. If the edit still lacks alpha, regenerate on a perfectly flat chroma-key background. Choose a key color absent from the subject: use pure blue `#0000FF` for teal or green hair, and pure green `#00FF00` for blue-heavy characters. Require a uniform fill with no texture, gradient, shadow, glow, or color spill. Then run:

```bash
scripts/chroma_key_to_alpha.swift blue key-source.png transparent-output.png
scripts/verify_transparency.swift transparent-output.png
```

Use `green` instead of `blue` when green is the safer key. The converter removes key-color spill only within a four-pixel band around transparent pixels so interior teal hair and cool shading remain intact.

Never extract a baked checkerboard by deleting bright neutral pixels: that can erase connected pale skin, white highlights, and silver costume details. Regenerate on a chroma-key background instead.

Visually inspect the converted PNG at normal size and about 500% zoom, preferably against both dark and light previews. Check the hair, hat ornaments, shoulders, fine chains, torn cape edges, and boots. Reject missing skin or silver details, opaque remnants, colored halos, cropped anatomy, duplicate limbs, or multiple characters. Make at most one targeted regeneration after the chroma-key fallback; if it still fails, report the concrete defect instead of claiming completion.

## Handoff

Save edits non-destructively with a clear suffix such as `-clean` unless the user explicitly asks to overwrite. Deliver only accepted PNGs, remove task-created failed intermediate exports from the output directory, and report dimensions and verified alpha status. Also state that the built-in image generator was used and provide the final prompt or a faithful concise prompt summary.
