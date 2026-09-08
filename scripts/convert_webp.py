"""
app/static/img/ 의 jpg/png 를 같은 이름의 .webp 로 변환 (원본은 유지).
실사진이 들어오면 실행. 템플릿은 jpg/png 를 참조하므로 webp 를 쓰려면
nginx 에서 Accept 헤더 기반 try_files 로 서빙하거나 (deploy/README.md 참고) 파일명을 바꿔 교체한다.

    python scripts/convert_webp.py            # 없는 것만
    python scripts/convert_webp.py --force    # 전부
    python scripts/convert_webp.py --max 1600 # 긴 변 1600px 로 리사이즈
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "app" / "static" / "img"


def main():
    force = "--force" in sys.argv
    mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 0
    n = 0
    for src in sorted(IMG.iterdir()):
        if src.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        dst = src.with_suffix(".webp")
        if dst.exists() and not force:
            continue
        im = Image.open(src)
        if mx and max(im.size) > mx:
            im.thumbnail((mx, mx))
        im.save(dst, "WEBP", quality=80, method=6)
        n += 1
        print(f"{src.name} -> {dst.name}  {src.stat().st_size // 1024}KB -> {dst.stat().st_size // 1024}KB")
    print("done:", n)


if __name__ == "__main__":
    main()
