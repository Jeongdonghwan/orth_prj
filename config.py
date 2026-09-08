"""
앱 설정 + 병원 정보(CLINIC).
병원명·전화·주소·진료시간은 이 파일의 CLINIC dict 한 곳에서만 관리한다.
비밀값(키·DB 접속정보)은 .env 에서 읽는다. (.env.example 참고)
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _env(key, default=""):
    v = os.environ.get(key)
    return default if v is None or v.strip() == "" else v.strip()


def _float_or_none(key):
    try:
        return float(_env(key))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# 병원 정보 — 확정되면 여기만 바꾼다. [ ] 는 미정 placeholder.
# ---------------------------------------------------------------------------
CLINIC = {
    "name": "운남튼튼마취통증의학과",   # 정식 명칭 (로고·타이틀·푸터)
    "short": "운남튼튼",              # 짧은 이름 (히어로 kicker, 비수술 섹션 제목)
    "en": "UNNAM TUNTUN PAIN CLINIC",
    "mark": "OO",                     # 텍스트 마크 (현재 헤더는 img/logo-mark.png 사용)
    "region": "[지역명]",             # SEO: "[병원명] 마취통증의학과 [지역명]"
    "tel": "000.000.0000",            # 화면 표시용
    "tel_link": "0000000000",         # tel: 링크용 (숫자만)
    "fax": "[000-000-0000]",
    "address": "[도로명 주소, 층]",
    "address_road": "[도로명 주소]",  # JSON-LD streetAddress
    "city": "[시/군/구]",             # JSON-LD addressLocality
    "postal": "",                     # 우편번호
    "ceo": "[성명]",                  # 대표자
    "biz_no": "[000-00-00000]",       # 사업자등록번호
    "doctor": "[원장 성명]",          # 대표원장 성명
    "doctor_title": "대표원장",
    "email": _env("CLINIC_EMAIL"),    # 문의 접수 메일 수신 주소 (선택)
    "blog_url": _env("CLINIC_BLOG_URL", "#"),
    "hours": [
        # (label, time, note)  — note 없으면 ""
        {"label": "평 일", "time": "AM 08:30 ~ PM 18:30", "note": ""},
        {"label": "점심시간", "time": "PM 01:00 ~ PM 02:00", "note": ""},
        {"label": "토요일", "time": "AM 08:30 ~ PM 13:30", "note": "(점심시간 없음)"},
    ],
    # JSON-LD openingHoursSpecification 용 구조화 데이터
    "opening_hours": [
        {"days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:30", "closes": "18:30"},
        {"days": ["Saturday"], "opens": "08:30", "closes": "13:30"},
    ],
    "closed": "일요일·공휴일 휴진",
    "parking": "[건물 지하주차장 무료]",
    "lat": _float_or_none("CLINIC_LAT"),
    "lng": _float_or_none("CLINIC_LNG"),
}


def _database_uri():
    """DATABASE_URL 우선. 없으면 DB_* 조합. 그것도 없으면 로컬 sqlite (개발용)."""
    url = _env("DATABASE_URL")
    if url:
        return url
    name = _env("DB_NAME")
    if name:
        return "mysql+pymysql://{u}:{p}@{h}:{port}/{n}?charset=utf8mb4".format(
            u=_env("DB_USER", name), p=_env("DB_PASSWORD", ""),
            h=_env("DB_HOST", "localhost"), port=_env("DB_PORT", "3306"), n=name)
    inst = BASE_DIR / "instance"
    inst.mkdir(exist_ok=True)
    return "sqlite:///" + str(inst / "ortho.sqlite").replace("\\", "/")


class Config:
    ENV = _env("FLASK_ENV", "production")
    DEBUG = ENV == "development"
    SECRET_KEY = _env("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    JSON_AS_ASCII = False

    SITE_URL = _env("SITE_URL", "http://localhost:5000").rstrip("/")
    KAKAO_JS_KEY = _env("KAKAO_JS_KEY")
    NAVER_SITE_VERIFICATION = _env("NAVER_SITE_VERIFICATION")

    # 관리자 (Basic Auth). ADMIN_PW 비어 있으면 /admin 접근 차단.
    ADMIN_ID = _env("ADMIN_ID", "admin")
    ADMIN_PW = _env("ADMIN_PW")

    # 문의 접수 메일 (선택) — SMTP_HOST 없으면 발송 생략
    SMTP_HOST = _env("SMTP_HOST")
    SMTP_PORT = int(_env("SMTP_PORT", "587"))
    SMTP_USER = _env("SMTP_USER")
    SMTP_PASSWORD = _env("SMTP_PASSWORD")
    SMTP_FROM = _env("SMTP_FROM", _env("SMTP_USER"))

    # 문의 rate limit: IP당 RATE_WINDOW초 안에 RATE_MAX회
    RATE_WINDOW = 300
    RATE_MAX = 3

    CLINIC = CLINIC
