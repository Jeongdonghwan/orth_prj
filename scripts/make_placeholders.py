"""
회색 더미 이미지 생성 — docs/03 체크리스트 파일명과 1:1.
실사진이 들어오면 같은 파일명으로 app/static/img/ 에 덮어쓰기만 하면 된다.

    python scripts/make_placeholders.py            # 없는 파일만 생성
    python scripts/make_placeholders.py --force    # 전부 다시 생성
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "static" / "img"

GRAY = "#D6DCDF"      # prototype .ph 배경
GRAY_TXT = "#7d878c"  # prototype .ph 글자

# (파일명, 가로, 세로, 배경색) — 배경형 사진은 prototype 에서 쓴 어두운 톤 유지 (흰 글자 가독성)
FILES = [
    ("hero.jpg",           1600, 900,  "#4c5c62"),
    ("doctor-bg.jpg",      1600, 900,  "#33515b"),
    ("doctor-main.png",    800,  1040, "#5b6f76"),
    ("surgery-1.jpg",      1600, 900,  GRAY),
    ("surgery-2.jpg",      1600, 900,  GRAY),
    ("surgery-3.jpg",      1600, 900,  GRAY),
    ("nonsurgical-bg.jpg", 1600, 900,  "#2a444d"),
    ("tour-main.jpg",      1600, 900,  GRAY),
    ("tour-1.jpg",         1600, 900,  GRAY),
    ("tour-2.jpg",         1600, 900,  GRAY),
    ("tour-3.jpg",         1600, 900,  GRAY),
    ("tour-4.jpg",         1600, 900,  GRAY),
    ("tour-5.jpg",         1600, 900,  GRAY),
    ("tour-6.jpg",         1600, 900,  GRAY),
    ("about-greeting.jpg", 1600, 900,  GRAY),
    ("og-image.jpg",       1200, 630,  "#1F3B45"),
]


def _font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf", "malgun.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make(name, w, h, bg, force=False):
    path = OUT / name
    if path.exists() and not force:
        return False
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    txt_color = GRAY_TXT if bg == GRAY else "#c7d0d4"
    font = _font(max(18, w // 40))
    small = _font(max(14, w // 70))
    bbox = d.textbbox((0, 0), name, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if bg == GRAY:  # 회색 더미: 가운데 파일명 (prototype .ph 와 같은 느낌)
        d.text(((w - tw) / 2, (h - th) / 2), name, fill=txt_color, font=font)
    # 모든 더미: 우하단 소형 라벨 (배경형 사진은 본문 글자 가독성을 위해 이것만)
    lbl = name + " · placeholder"
    d.text((w - 20 - d.textlength(lbl, font=small), h - 20 - th), lbl, fill=txt_color, font=small)
    if name.lower().endswith(".png"):
        img.save(path, "PNG", optimize=True)
    else:
        img.save(path, "JPEG", quality=70, optimize=True)
    return True


def main():
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for name, w, h, bg in FILES:
        if make(name, w, h, bg, force):
            made += 1
            print("made", name)
    print(f"done: {made} created, {len(FILES) - made} kept")


if __name__ == "__main__":
    main()
