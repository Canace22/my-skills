---
name: web-style-clone
description: Analyze and replicate the visual design language of a reference webpage. Use when user says "clone this design", "copy this style", "replicate this UI", "match this website's look", "extract design tokens", or provides a URL and asks to match its visual style. Extracts design tokens and systems, does NOT copy assets.
---

# Web Style Clone

## Overview

Replicate the **design language and visual system** of a reference webpage.

- Does NOT copy assets or brand logos.
- Extracts reusable design rules.
- Goal: 80–95% visual fidelity with scalable architecture.

---

## Workflow

### Step 1 — Layout Decomposition

Analyze page structure, then output:

```json
{
  "layout_type": "centered | full-width | split",
  "max_width": "1200px",
  "grid_system": "12-column",
  "section_spacing": "80px"
}
```

Identify: Hero / Sections / CTA / Footer, container width, grid, alignment.

---

### Step 2 — Design Token Extraction

Extract colors, typography, and spacing, then output:

```json
{
  "colors": {
    "primary": "#635BFF",
    "secondary": "...",
    "background": "#0F172A",
    "text_primary": "#FFFFFF",
    "hover": "..."
  },
  "typography": {
    "font_family": "Inter",
    "h1": "48px", "h2": "...", "h3": "...",
    "body": "16px",
    "line_height_ratio": 1.5,
    "weights": [400, 600, 700]
  },
  "spacing": {
    "base_unit": 8,
    "section_gap": "80px",
    "component_padding": "..."
  }
}
```

---

### Step 3 — Component System Analysis

Identify and document:

- Button variants (primary, secondary, ghost)
- Card styles (border, shadow, radius)
- Input styles
- Navbar structure
- Global border-radius rules
- Shadow scale (sm / md / lg)

---

### Step 4 — Motion & Interaction

Extract transition behavior:

```json
{
  "duration_fast": "150ms",
  "duration_normal": "250ms",
  "easing": "cubic-bezier(0.4, 0, 0.2, 1)"
}
```

Note hover effects, entrance animations, and micro-interactions.

---

## Fidelity Levels

| Level  | Description                    |
|--------|--------------------------------|
| Low    | Style-inspired                 |
| Medium | Visually close                 |
| High   | Pixel-level approximation      |

Ask the user which level to target before generating code.

---

## Compliance Rules

- Do NOT copy copyrighted assets or brand logos.
- Extract design language only — color values, spacing, font choices, motion curves.

---

## Output

After analysis, produce:

1. A design token file (`tokens.json` or CSS variables)
2. A component style guide (buttons, cards, inputs)
3. Implementation code matching the project's stack (React/CSS/Tailwind/etc.)

Cloning a page is not copying its code: abstract the design system, distill the design language, and deliver an implementation that scales.
