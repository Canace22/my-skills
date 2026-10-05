---
name: ui-styling-patterns
description: "Patterns for styling React UI panels: converting overlays to sidebars, compact layouts, design token usage, unified button colors, icon-only action bars and dropdown menus. Use when restyling a panel or sidebar, when the user says the buttons are too colorful or the layout is too loose, or when a component must match the global design system."
---

# UI Styling Patterns

## Overview

Reusable patterns for styling React app UI panels, with emphasis on design token consistency and compact layouts. Applicable when working on sidebar panels, chat interfaces, or any UI component that needs to match a global design system.

## Key Patterns

### 1. Sidebar Layout Conversion

When converting an overlay/modal to a sidebar layout:

- Use `display: flex` on parent container
- Set `flex: none` on sidebar with `width: clamp(min, vw, max)`
- Add `border-left: 1px solid var(--color-border)` for visual separation
- Adjust padding to be more compact (use `var(--space-s)` instead of fixed px)

```css
.panel-dock--sidebar {
  flex: none;
  width: clamp(380px, 32vw, 560px);
  min-width: 340px;
  max-width: 560px;
  height: 100%;
  border-left: 1px solid var(--color-border);
  background: var(--color-bg-page);
}
```

### 2. Design Token Consistency

Always use CSS custom properties (design tokens) for:

- Colors: `var(--color-brand-primary)`, `var(--color-text-primary)`, etc.
- Spacing: `var(--space-s)`, `var(--space-m)`, etc.
- Border radius: `var(--radius-m)`, `var(--radius-l)`, etc.
- Shadows: `var(--shadow-soft)`, `var(--shadow-medium)`, etc.

**Avoid hardcoded color values.** Use `color-mix()` for hover states:
```css
background: color-mix(in srgb, var(--color-brand-primary) 12%, transparent);
```

### 3. Compact Sidebar Styling

For sidebar panels, reduce from overlay defaults:

- Padding: 16px → 8px (or use `var(--space-s)`)
- Title font: Use `var(--text-heading)` or smaller
- Buttons: 32px instead of 40px
- Remove unnecessary shadows and gradients

### 4. Auto-Resize Textarea

Pattern for auto-resizing textarea in React:
```jsx
<textarea
  rows={1}
  onInput={(e) => {
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  }}
/>
```

### 5. Color Unification

When multiple interactive elements exist in a panel:

- Use the same brand color family for all buttons
- Unify hover states with consistent opacity/color-mix
- Avoid rainbow colors unless there's a clear semantic meaning

```css
/* Unified hover state */
.button:hover {
  background: color-mix(in srgb, var(--color-brand-primary) 12%, transparent);
}
```

## Defaults

- Compact, unified styling in sidebar contexts
- Every color comes from the global design system
- Unify colorful buttons into one brand color family
- Smaller send buttons (32px) in chat interfaces

### 6. Compact Action Bar Pattern

When an action bar has too many buttons (3+), consolidate into icon-only layout:

- **Primary action**: Icon button (e.g., `+` for add) — no text
- **Secondary actions**: Collect into a `Dropdown` with `MoreHorizontal` icon trigger
- **Interactive indicators**: Clickable dots/circles with hover scale effect + tooltip
- **All Dropdown menu items must have icons** for visual consistency

```
Before (crowded):
[PrioritySelect] [DatePicker] [编辑] [复制] [移到待办] [删除]

After (compact):
[PriorityDot] [DatePicker] [⋯Menu]
```

Pattern for clickable priority indicator:
```jsx
<div
  className="priority-dot clickable"
  style={{ backgroundColor: getPriorityColor(priority) }}
  title={`点击切换 (当前: ${label})`}
  onClick={() => onCycle(priority)}
/>
```

```css
.priority-dot.clickable {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.priority-dot.clickable:hover {
  transform: scale(1.3);
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}
```

### 7. Preset-vs-Custom Select Pattern

When a config field has known preset values but also needs custom input:
- Preset providers: use `<select>` with `<option>` list
- Custom/unknown provider: fall back to `<input>` with placeholder
- Read available options from a data model (e.g., provider's model list), not hardcoded in the component

```jsx
{(() => {
  const provider = getProvider(providerId);
  const options = provider?.models ?? [];
  if (options.length > 0) {
    return (
      <label>模型
        <select value={cfg.model} onChange={...}>
          {options.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </label>
    );
  }
  return (
    <label>模型
      <input value={cfg.model} placeholder="输入模型名称" onChange={...} />
    </label>
  );
})()}
```

### 8. Ant Design Dropdown Menu Structure

When consolidating actions into a Dropdown menu:
- Use `trigger={['click']}` for click-to-open
- Each item needs: `key`, `label`, `icon`, `onClick`
- Add `{ type: 'divider' }` before destructive actions (delete)
- Set `danger: true` on destructive items
- Spread conditional items with `...(condition ? [{ ... }] : [])`

```jsx
<Dropdown
  menu={{
    items: [
      { key: 'edit', label: '编辑', icon: <Pencil size={14} />, onClick: onEdit },
      ...copyable ? [{ key: 'copy', label: '复制', icon: <Copy size={14} />, onClick: onCopy }] : [],
      { type: 'divider' },
      { key: 'delete', label: '删除', danger: true, icon: <Trash2 size={14} />, onClick: onDelete },
    ],
  }}
  trigger={['click']}
>
  <Button type="text" size="small" icon={<MoreHorizontal size={16} />} />
</Dropdown>
```

## Pitfalls

1. **Don't use hardcoded colors** when design tokens exist
2. **Don't leave rainbow colors** on buttons when they should be unified
3. **Don't use overlay-style padding** in sidebar contexts
4. **Remember to update hover states** when changing base colors
5. **Check responsive behavior** after sidebar layout changes
6. **React Fragment `<>` in flex containers breaks alignment** — fragments don't create a DOM node, so children become direct flex items of the parent. If you need a group of elements to stay together in a flex row, wrap them in a `<div>` (or the original wrapper), not a fragment. This is a common cause of unexpected alignment shifts.
7. **Dropdown menu items should all have icons** — mixing icon + text items looks inconsistent. If one item has an icon, all should.
8. **Prefer icon-only buttons** over text buttons in action bars. If a button says "Edit" or "Add", replace it with an icon + tooltip. Text buttons in compact panels feel cluttered.
9. **Section ordering matters** — check that the order of sections in a view matches the user's mental model, not just the order they were coded in.
10. **Auto-context features must check the current page** — when implementing "auto-reference current document" or similar context-aware UI, check which surface is active (editor vs dashboard, etc.) before showing context. Showing document references on non-editor pages confuses users. Gate visibility on the app's current-surface state.

## Verification

After styling changes:
1. Check that all colors use design tokens
2. Verify hover states are consistent
3. Test responsive behavior
4. Ensure sidebar layout doesn't break on smaller screens
