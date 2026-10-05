#!/usr/bin/env python3
"""统一视口整页截图：runs/*.html -> shots/*.png。

用法：python3 screenshot_html.py [runs_dir] [shots_dir] [width]
默认 runs/ -> shots/，视口宽 1280（height 800），full_page=True 整页截图。

自动探测浏览器（三级）：
1) 先试 playwright 默认版本；
2) 失败（"Executable doesn't exist at .../chromium_headless_shell-XXXX"）时
   回退到 ms-playwright 缓存里任意完整 chromium（macOS 路径），
   并显式 headless=True（指定 executable_path 后默认可能是 headed）；
3) 缓存里也没有 → macOS 系统 Chrome（/Applications/Google Chrome.app，
   2026-08-09 实测最稳：缓存 chromium 与 playwright 包协议不匹配时仍可用）。
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SYSTEM_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def find_chromium_fallback():
    """在 ~/Library/Caches/ms-playwright 里找最大的完整 chromium 可执行文件。"""
    cache = Path.home() / "Library/Caches/ms-playwright"
    if not cache.is_dir():
        return None
    for rev in sorted(cache.glob("chromium-*"), reverse=True):
        exe = (rev / "chrome-mac-arm64"
               / "Google Chrome for Testing.app"
               / "Contents/MacOS" / "Google Chrome for Testing")
        if exe.exists():
            return str(exe)
    return None


def find_system_chrome():
    return SYSTEM_CHROME if Path(SYSTEM_CHROME).exists() else None


def main():
    runs_dir = sys.argv[1] if len(sys.argv) > 1 else "runs"
    shots_dir = sys.argv[2] if len(sys.argv) > 2 else "shots"
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    Path(shots_dir).mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            exe = find_chromium_fallback() or find_system_chrome()
            if not exe:
                raise
            print("[fallback] using browser at", exe)
            b = p.chromium.launch(executable_path=exe, headless=True)
        pg = b.new_page(viewport={"width": width, "height": 800})
        for f in sorted(Path(runs_dir).glob("*.html")):
            pg.goto(f.resolve().as_uri())
            pg.wait_for_load_state("networkidle")
            pg.screenshot(path="{}/{}".format(shots_dir, f.stem + ".png"), full_page=True)
            print("shot:", f.stem)
        b.close()


if __name__ == "__main__":
    main()
