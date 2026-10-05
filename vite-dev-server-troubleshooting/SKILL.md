---
name: vite-dev-server-troubleshooting
description: "Diagnose browser-side errors when running a Vite dev server: stale pages after dependency re-optimization, the HMR websocket connecting to the wrong port when several dev servers run, and duplicate library instances (e.g. \"Multiple instances of Three.js\"). Use when the user opens a Vite dev URL and says the console is full of errors, the page renders broken, or errors cite code that is not in the source."
---

# Vite dev server troubleshooting

Trigger: the user opens a Vite dev URL and reports a console full of errors ("一堆错误"), or a broken render.

## Diagnostic order (each step read-only)

1. **Server logs first** — read the dev server's terminal output (or its background-process log). Look for:
   - `Port 5173 is in use, trying another one...` → port churn, multiple dev servers alive
   - `Re-optimizing dependencies because vite config has changed` → **prebuild invalidated while a page was open**
2. **Curl the page + entry modules** — `curl -s http://127.0.0.1:PORT/` (title tells you which project), then curl `/src/main.js` etc. All 200 + no server-side compile error = the problem is browser-side runtime.
3. **Check which ports are what** — multiple Vite servers run simultaneously (5173/5174/5175). A dead/hung process can occupy a port silently (`curl` returns nothing but port is "in use").
4. **Inspect the prebuild cache** — `ls node_modules/.vite/deps/ | grep -i three`:
   - TWO entries (e.g. `three.js` AND `three.module-XXXX.js`) = duplicate module instances. Causes `THREE.WARNING: Multiple instances of Three.js being imported` and runtime `TypeError: ... reading 'setFromMatrixPosition'` etc.
   - Compare the `?v=` query the running server serves vs what the user's open page requests (visible in the error stack, e.g. `three.module-BEvS_7fE.js?v=3321a04f`).
5. **Cross-check error line numbers against source** — grep the source for the failing API. If the line numbers match your source but the API call doesn't exist there, or the source file is small but errors cite 9000+ lines, **the browser is executing a stale dependency graph**, not current code.

## Root causes & fixes

### Stale page after dependency re-optimization (most common)
Vite re-prebuilds when config/deps change; the open page keeps referencing old `?v=` hashes and the old module copies. HMR usually force-reloads, but **if the HMR websocket is also failing, the page stays stuck on the stale graph forever** → floods console with `Failed to send error to Vite server` + `Uncaught TypeError` that don't exist in current code.
- **Fix #1 (try first): hard refresh** — user does `Cmd+Shift+R`. New page loads the new prebuild, errors usually vanish.
- **Fix #2 (durable):** avoid re-prebuild churn — pin versions, or clear `node_modules/.vite` + restart once.

### HMR websocket connecting to wrong port
When several Vite servers are up and ports shift (5173→5175), the client may try the wrong server (`(browser) 127.0.0.1:5175/ <— WebSocket (failing) -> 127.0.0.1:5173/`). Console noise: repeated `WebSocket connection to 'ws://...' failed`. Often secondary to the stale-page problem — fix the stale page first.

### Duplicate library instances (e.g. Three.js)
`THREE.WARNING: Multiple instances` + undefined-method TypeErrors = two module copies in the graph (two prebuild entries, or mixed import paths like `three` vs `three/build/three.module.js`).
- Inspect imports: `grep -rn "three/build|three\.module" src/` — zero matches doesn't rule it out; check `.vite/deps` for two hashed copies.
- Fix: `resolve: { dedupe: ['three'] }` + `optimizeDeps: { include: ['three'] }` in `vite.config.js`, then clear `node_modules/.vite` and restart.

## Pitfalls

- Don't take browser-console output as current-code truth when a re-optimization + port-shift happened mid-session. Serve-side logs are the ground truth for "what code is actually served".
- Don't blind-debug duplicate-instance errors before checking whether the user just needs a hard refresh — half the console noise disappears with it.
- A project can be a huge single-file app (e.g. `src/main.js` 9,700 lines) — line numbers in errors are valid; use them, but verify the API exists in the source before assuming a code bug.
