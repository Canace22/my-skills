---
name: image-ocr-macos
description: "Read text out of screenshots or images on macOS with the system Vision framework when the model has no vision ability — no pip installs, no tesseract, works offline. Use when the user sends a screenshot you cannot see, says 「看这张图」「我发了一张图」, or you need error text, numbers, or labels from an image."
---

# Image OCR on macOS (Vision framework)

## Trigger

- User sends a screenshot but the model or platform cannot see images.
- User says "我发了一张图" / "看这张图" and the content matters (error console, a table of numbers, UI state).
- You need to read error text, numbers, or labels out of an image.

## Step 0 — Locate the image

Use the path the user gives. If they say they sent an image you never saw, look in the tool's image cache — chat gateways often save incoming images there without surfacing them in the conversation. For example, Hermes saves Telegram images to `~/.hermes/cache/images/`:

```bash
ls -lat ~/.hermes/cache/images/ | head
```

Take the newest `.jpg`/`.png` unless the user's description matches an older one.

## Step 1 — OCR with the bundled script

```bash
swift <skill-dir>/scripts/ocr.swift <image-path>
```

First run compiles Swift; allow up to ~60s. The script prints recognized lines in reading order (top→bottom, roughly left→right).

## Step 2 — Sanity-check what matters

- **For code/error text**: OCR is usually accurate enough to identify the error string; then grep the actual source to confirm the symptom.
- **For numbers (prices, amounts, statistics)**: OCR can scramble digits and drop separators (e.g. `4,032.02` read as `4032.02`, `91,320.32` as `91320.32`, `19.515` vs `19.515` ok but `567.754` vs `563.30` ambiguous). Cross-validate against an authoritative source when possible (an API, a config file, the original data) — never update a record from OCR alone if it contradicts the existing truth source without flagging it.
- Column layout can mis-pair labels and values (e.g. which cost pairs with which price). Reconstruct the pairing by arithmetic when possible (value × shares ≈ market cap; (price − cost)/cost ≈ pct).

## Pitfalls

1. The image may be re-delivered twice (same path) — dedupe by filename before re-OCR.
2. `swift` needs a moment to compile on first run; don't kill it at the 15s mark.
3. If OCR output is empty, the image may be mostly graphics (photos, charts) — Vision text recognition only reads text-like strokes.
4. Reading a screenshot of an app with its own table layout: the OCR order follows visual rows, so group by row, not by consecutive lines.

## Support files

- `scripts/ocr.swift` — standalone Vision-framework OCR (zh-Hans + en-US, accurate level).
