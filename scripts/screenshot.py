"""
페이지 스크린샷 (Playwright/Chromium). 서버가 떠 있어야 한다.

    python scripts/screenshot.py <out_dir> [path ...]
    예) python scripts/screenshot.py screenshots/phase1 /
        python scripts/screenshot.py screenshots/phase2 / /about /doctor "/clinic?tab=spine" /location
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

import os
BASE = "http://127.0.0.1:" + os.environ.get("PORT", "5000")
WIDTHS = {"desktop": 1440, "mobile": 375}


def slug(path):
    s = path.strip("/").replace("/", "_").replace("?", "_").replace("=", "-") or "index"
    return s


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "screenshots")
    paths = sys.argv[2:] or ["/"]
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, w in WIDTHS.items():
            ctx = browser.new_context(viewport={"width": w, "height": 900}, device_scale_factor=1,
                                      is_mobile=(w < 640), has_touch=(w < 640))
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            for path in paths:
                page.goto(BASE + path, wait_until="networkidle")
                # 스크롤 리빌 트리거: 끝까지 단계적으로 스크롤한 뒤 맨 위로
                total = page.evaluate("document.documentElement.scrollHeight")
                for y in range(0, total, 500):
                    page.evaluate(f"scrollTo({{top:{y},behavior:'instant'}})"); page.wait_for_timeout(120)
                page.evaluate("scrollTo({top:0,behavior:'instant'})")
                page.wait_for_timeout(1200)  # hero fade + reveal transition
                f = out / f"{slug(path)}_{name}.png"
                page.screenshot(path=str(f), full_page=True)
                print("saved", f, page.evaluate("document.documentElement.scrollWidth"), "px wide /",
                      page.evaluate("document.documentElement.scrollHeight"), "px tall")
            if errors:
                print(f"[{name}] console/page errors:")
                for e in errors:
                    print("   ", e)
            ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
