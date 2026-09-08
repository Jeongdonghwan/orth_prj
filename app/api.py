"""POST /api/inquiry — 상담문의 저장 (서버측 검증 + IP rate limit + honeypot + 선택 메일 발송)"""
import logging
import re
import smtplib
import threading
import time
from collections import defaultdict, deque
from email.message import EmailMessage

from flask import Blueprint, current_app, jsonify, request

from .models import Inquiry, db

bp = Blueprint("api", __name__, url_prefix="/api")
log = logging.getLogger(__name__)

PARTS = ("목", "허리", "무릎", "어깨", "기타")
_hits = defaultdict(deque)   # ip -> 최근 요청 시각들 (프로세스 메모리; gunicorn 워커별)
_lock = threading.Lock()


def client_ip():
    xff = request.headers.get("X-Forwarded-For", "")
    return (xff.split(",")[0].strip() if xff else request.remote_addr) or ""


def rate_limited(ip):
    win = current_app.config["RATE_WINDOW"]
    mx = current_app.config["RATE_MAX"]
    now = time.time()
    with _lock:
        q = _hits[ip]
        while q and now - q[0] > win:
            q.popleft()
        if len(q) >= mx:
            return True
        q.append(now)
    return False


def _bad(msg, code=400):
    return jsonify(ok=False, message=msg), code


@bp.post("/inquiry")
def inquiry():
    data = request.get_json(silent=True) or request.form.to_dict() or {}

    # honeypot: 봇이 채우면 조용히 성공한 척
    if (data.get("website") or "").strip():
        return jsonify(ok=True, message="접수되었습니다. 확인 후 연락드리겠습니다.")

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    part = (data.get("part") or "").strip()
    message = (data.get("message") or "").strip()
    agree = data.get("agree") in (True, "true", "on", "1", 1, "y")

    if not (2 <= len(name) <= 50):
        return _bad("이름을 확인해 주세요.")
    digits = re.sub(r"\D", "", phone)
    if not (9 <= len(digits) <= 11) or len(phone) > 20:
        return _bad("연락처를 확인해 주세요.")
    if part not in PARTS:
        part = "기타"
    if len(message) > 2000:
        return _bad("문의 내용은 2000자 이내로 적어 주세요.")
    if not agree:
        return _bad("개인정보 수집·이용에 동의해 주세요.")

    ip = client_ip()
    if rate_limited(ip):
        return _bad("잠시 후 다시 시도해 주세요. (5분에 3회까지 접수 가능)", 429)

    if not current_app.config.get("DB_OK"):
        return _bad("현재 온라인 접수가 어렵습니다. 전화로 문의해 주세요.", 503)

    row = Inquiry(name=name, phone=phone, part=part, message=message, ip=ip)
    try:
        db.session.add(row)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.exception("inquiry save failed: %s", e)
        return _bad("접수 중 오류가 발생했습니다. 전화로 문의해 주세요.", 500)

    _notify_async(current_app._get_current_object(), row.to_row())
    return jsonify(ok=True, id=row.id, message="접수되었습니다. 확인 후 연락드리겠습니다.")


# ---------------- 메일 발송 (선택) ----------------
def _notify_async(app, row):
    cfg = app.config
    to = cfg["CLINIC"].get("email")
    if not (cfg.get("SMTP_HOST") and to):
        return
    threading.Thread(target=_send_mail, args=(cfg, to, row), daemon=True).start()


def _send_mail(cfg, to, row):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"[홈페이지 상담문의] {row['name']} / {row['part']}"
        msg["From"] = cfg["SMTP_FROM"] or cfg["SMTP_USER"]
        msg["To"] = to
        msg.set_content(
            "이름: {name}\n연락처: {phone}\n증상 부위: {part}\n접수시각: {created_at}\n\n{message}\n".format(**row)
        )
        with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=15) as s:
            s.ehlo()
            if cfg["SMTP_PORT"] != 25:
                s.starttls()
            if cfg["SMTP_USER"]:
                s.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            s.send_message(msg)
    except Exception as e:
        log.warning("inquiry mail failed: %s", e)
