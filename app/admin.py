"""/admin/inquiries — Basic Auth, 최신순 목록, 읽음 처리, 삭제, CSV 다운로드"""
import csv
import io
from datetime import datetime
from functools import wraps

from flask import (Blueprint, Response, abort, current_app, redirect, render_template,
                   request, url_for)

from .models import Inquiry, db

bp = Blueprint("admin", __name__, url_prefix="/admin")
PER_PAGE = 30


def _auth_required():
    return Response("로그인이 필요합니다.", 401,
                    {"WWW-Authenticate": 'Basic realm="admin", charset="UTF-8"'})


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        pw = current_app.config.get("ADMIN_PW")
        if not pw:
            abort(403, "관리자 비밀번호(ADMIN_PW)가 설정되지 않았습니다.")
        auth = request.authorization
        if not auth or auth.type != "basic" or auth.username != current_app.config["ADMIN_ID"] or auth.password != pw:
            return _auth_required()
        if not current_app.config.get("DB_OK"):
            abort(503, "DB에 연결할 수 없습니다.")
        return fn(*a, **kw)
    return wrapper


@bp.route("/")
@bp.route("/inquiries")
@login_required
def inquiries():
    page = max(1, request.args.get("page", 1, type=int))
    q = (request.args.get("q") or "").strip()
    only_unread = request.args.get("unread") == "1"
    query = Inquiry.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Inquiry.name.like(like), Inquiry.phone.like(like), Inquiry.message.like(like)))
    if only_unread:
        query = query.filter(Inquiry.is_read.is_(False))
    total = query.count()
    unread = Inquiry.query.filter(Inquiry.is_read.is_(False)).count()
    rows = (query.order_by(Inquiry.created_at.desc(), Inquiry.id.desc())
                 .offset((page - 1) * PER_PAGE).limit(PER_PAGE).all())
    pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    return render_template("admin/inquiries.html", rows=rows, page=page, pages=pages,
                           total=total, unread=unread, q=q, only_unread=only_unread)


@bp.post("/inquiries/<int:iid>/read")
@login_required
def mark_read(iid):
    row = Inquiry.query.get_or_404(iid)
    row.is_read = not row.is_read
    db.session.commit()
    return redirect(request.referrer or url_for("admin.inquiries"))


@bp.post("/inquiries/<int:iid>/delete")
@login_required
def delete(iid):
    row = Inquiry.query.get_or_404(iid)
    db.session.delete(row)
    db.session.commit()
    return redirect(request.referrer or url_for("admin.inquiries"))


@bp.route("/inquiries.csv")
@login_required
def export_csv():
    rows = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "접수시각", "이름", "연락처", "부위", "내용", "IP", "읽음"])
    for r in rows:
        d = r.to_row()
        w.writerow([d["id"], d["created_at"], d["name"], d["phone"], d["part"], d["message"], d["ip"], d["is_read"]])
    out = "﻿" + buf.getvalue()  # BOM: 엑셀 한글 깨짐 방지
    fname = f"inquiries_{datetime.now():%Y%m%d}.csv"
    return Response(out, mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})
