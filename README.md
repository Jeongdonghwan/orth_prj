# 운남튼튼마취통증의학과 홈페이지 개발 패키지

읽는 순서
1. docs/01_기획서.md — 사이트맵·섹션·원고·의료광고 문구 규칙
2. docs/02_디자인가이드.md — 색/타이포/컴포넌트
3. docs/03_콘텐츠_에셋_체크리스트.md — 클라이언트에게 받을 것 (파일명 고정)
4. docs/04_개발명세.md — 클로드코드 Phase 1~4
5. prototype/index.html — 디자인 확정본 (브라우저로 열어서 확인)
6. CLAUDE.md — 클로드코드 프로젝트 루트에 그대로 복사

---

## 로컬 실행

```bash
pip install -r requirements.txt
cp .env.example .env            # 값 비워 둬도 실행됨 (DB는 instance/ortho.sqlite 로 대체)
python scripts/make_placeholders.py   # 회색 더미 생성 (없는 파일만). 현재는 스톡 사진이 들어 있어 보통 불필요
python run.py                   # http://127.0.0.1:5000  (포트 변경: PORT=5077 python run.py)
```

- 관리자: `http://127.0.0.1:5000/admin/inquiries` — `.env`의 `ADMIN_ID` / `ADMIN_PW` 로 Basic Auth. `ADMIN_PW` 가 비어 있으면 403.
- 카카오맵: `KAKAO_JS_KEY` + `CLINIC_LAT` / `CLINIC_LNG` 세 값이 모두 있어야 지도가 뜨고, 없으면 회색 안내 박스.
- 스크린샷 검증: 서버 띄운 뒤 `PORT=5000 python scripts/screenshot.py screenshots / /about /doctor "/clinic?tab=spine" /location`

## 디자인 (v2, 2026-09-03)

- 팔레트는 `운남튼튼-로고.ai` 의 네이비 `#1E2188` / 블루 `#005BAC` 기준. `style.css` 상단 `:root` 변수만 바꾸면 전체 색이 바뀐다.
- 모션: 히어로 3장 크로스페이드+켄번즈, 스크롤 리빌(`.rv` → `.in`, IntersectionObserver), 카드 호버, 헤더 스크롤 축소, 탭 페이드. `prefers-reduced-motion` 이면 전부 꺼진다.
- 사진은 전부 Pexels 무료 스톡 임시본 → `docs/03_콘텐츠_에셋_체크리스트.md` 파일명 그대로 교체. 원본 다운로드·크롭은 `scripts/` 가 아니라 세션에서 수동으로 했으므로, 재생성이 필요하면 같은 이름·규격(1600×900 등)으로 만들면 된다.
- 로고: 헤더/푸터는 마크(`logo-mark.png`)+타이포. 워드마크 전체(`logo.png`, `logo-white.png`)는 "마취통증의학과" 표기라 쓰지 않았다. 전체 로고를 쓰려면 `base.html` 의 `.logo` 안 `<img>`+`<span>` 을 `logo.png` 한 장으로 바꾸면 된다.
- 스크린샷: `screenshots/v2/` (리디자인), `screenshots/final/` (프로토타입 그대로 옮긴 v1).

## 병원 정보 수정

`config.py` 의 `CLINIC` dict 한 곳만 수정한다 (병원명·전화·주소·진료시간·대표자·사업자번호·원장 성명). 템플릿은 `{{ clinic.* }}` 로만 참조한다.

## 구조

```
app/
  __init__.py     create_app(), context_processor(clinic, map_link, jsonld…), 404
  routes.py       / /about /doctor /clinic?tab= /location /sitemap.xml /robots.txt
  api.py          POST /api/inquiry (검증·rate limit·honeypot·메일)
  admin.py        /admin/inquiries (Basic Auth, 검색, 읽음, 삭제, CSV)
  models.py       Inquiry
  templates/      base, _macros(섹션 매크로), index, about, doctor, clinic, location, 404, admin/
  static/         css/style.css(prototype 그대로 + 하단 추가분), js/main.js, img/(더미), svg/
config.py         Config + CLINIC
run.py / wsgi.py  개발 실행 / gunicorn 진입점
scripts/          make_placeholders.py, convert_webp.py, screenshot.py
deploy/           ortho.service, nginx.conf, schema.sql, README.md(카페24 배포 순서)
```

## 의료광고 문구 검사

```bash
grep -rnE "최고|유일|완치|100%|부작용 없" app/templates config.py
```
