# 정형외과 홈페이지 — CLAUDE.md

## 프로젝트 개요
- 클라이언트: [병원명]정형외과의원 (placeholder — 확정 시 전체 치환)
- 목적: 원페이지 스크롤형 병원 홈페이지 + 서브페이지 4개
- 레퍼런스: 당진효자정형외과의원 사이트의 **섹션 구조·정보 위계**만 참고. 문구·사진·로고·일러스트는 절대 재사용하지 않음 (저작권). 모든 카피는 `docs/01_기획서.md`의 원고 사용.
- 디자인 확정본: `prototype/index.html` — 이 파일의 룩을 그대로 Jinja2 템플릿으로 옮긴다. 임의로 디자인을 바꾸지 말 것.

## 기술 스택 (고정)
- Python 3.11 / Flask 3.x / Jinja2 SSR
- MariaDB (문의·예약 저장용, 최소 테이블)
- 배포: Cafe24 가상서버, gunicorn + nginx
- 프론트: 순수 HTML/CSS/JS. 프레임워크·빌드툴 없음. Tailwind 금지.
- 폰트: Pretendard (CDN, `https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css`)
- 지도: 카카오맵 JavaScript SDK (appkey는 `.env` → `KAKAO_JS_KEY`)

## 디렉토리 구조
```
app/
  __init__.py        # create_app()
  routes.py          # 페이지 라우트
  api.py             # /api/inquiry POST
  models.py          # Inquiry 모델 (SQLAlchemy)
  templates/
    base.html        # head, header, quick-menu, footer
    index.html       # 메인 (섹션 9개)
    about.html       # 병원소개
    doctor.html      # 의료진소개
    clinic.html      # 클리닉 상세 (?tab=spine|joint|nonsurgical|manual)
    location.html    # 오시는길
  static/
    css/style.css    # prototype의 <style> 그대로 분리
    js/main.js       # prototype의 <script> 그대로 분리
    img/             # 클라이언트 실사진 (현재는 placeholder)
    svg/             # 의학 일러스트·아이콘 (prototype/assets/svg 복사)
config.py
run.py
requirements.txt
.env.example
```

## 페이지·라우트
| 경로 | 템플릿 | 비고 |
|---|---|---|
| `/` | index.html | 메인 원페이지 |
| `/about` | about.html | 병원소개 (인사말 + 병원 둘러보기 전체) |
| `/doctor` | doctor.html | 의료진 소개 |
| `/clinic` | clinic.html | 4개 클리닉 탭 |
| `/location` | location.html | 진료시간 + 카카오맵 + 주차안내 |
| `POST /api/inquiry` | — | 상담문의 저장, JSON 응답 |

## 개발 규칙
1. **한 Phase씩** 진행하고 멈춰서 확인받는다. 다음 Phase로 자동 진행 금지.
2. 카피·색·간격은 prototype/index.html과 `docs/02_디자인가이드.md` 기준. 새 색상·새 폰트 추가 금지.
3. 이미지 경로는 `static/img/` 아래 placeholder 파일명 유지 (`docs/03_콘텐츠_에셋_체크리스트.md`의 파일명과 1:1). 실사진 들어오면 파일만 교체.
4. 애니메이션은 prototype에 있는 것만 (히어로 1회 페이드, 탭/슬라이드 전환). 스크롤 리빌 추가 금지.
5. 모바일(375px)에서 깨지는지 매 Phase마다 확인.
6. 의료광고 심의 관련 문구 규칙 (`docs/01_기획서.md` 하단) 위반 문구 생성 금지.

## Phase 계획 (docs/04_개발명세.md 상세)
- Phase 1: Flask 뼈대 + base.html + 메인 index.html 정적 완성
- Phase 2: 서브페이지 4개
- Phase 3: 카카오맵 + 상담문의 폼/DB + 관리자 조회
- Phase 4: SEO(메타/OG/sitemap/robots/네이버 웹마스터) + 배포 스크립트

## 환경변수 (.env.example)
```
FLASK_ENV=production
SECRET_KEY=
DATABASE_URL=mysql+pymysql://user:pw@localhost/ortho
KAKAO_JS_KEY=
CLINIC_LAT=
CLINIC_LNG=
```
