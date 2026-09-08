from flask import Blueprint, Response, current_app, render_template, request, url_for

bp = Blueprint("pages", __name__)

CLINIC_TABS = ("spine", "joint", "nonsurgical", "manual")


@bp.route("/")
def index():
    return render_template("index.html", page_id="index")


@bp.route("/about")
def about():
    return render_template("about.html", page_id="about")


@bp.route("/doctor")
def doctor():
    return render_template("doctor.html", page_id="doctor")


@bp.route("/clinic")
def clinic():
    tab = request.args.get("tab", "spine")
    if tab not in CLINIC_TABS:
        tab = "spine"
    return render_template("clinic.html", page_id="clinic", active_tab=tab)


@bp.route("/location")
def location():
    return render_template("location.html", page_id="location")


# ---------------- SEO ----------------
@bp.route("/sitemap.xml")
def sitemap():
    base = current_app.config["SITE_URL"]
    urls = [
        (url_for("pages.index"), "1.0"),
        (url_for("pages.about"), "0.8"),
        (url_for("pages.doctor"), "0.8"),
        (url_for("pages.clinic", tab="spine"), "0.8"),
        (url_for("pages.clinic", tab="joint"), "0.7"),
        (url_for("pages.clinic", tab="nonsurgical"), "0.7"),
        (url_for("pages.clinic", tab="manual"), "0.7"),
        (url_for("pages.location"), "0.8"),
    ]
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio in urls:
        body.append(f"  <url><loc>{base}{path.replace('&', '&amp;')}</loc><priority>{prio}</priority></url>")
    body.append("</urlset>")
    return Response("\n".join(body), mimetype="application/xml")


@bp.route("/robots.txt")
def robots():
    base = current_app.config["SITE_URL"]
    txt = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {}/sitemap.xml\n".format(base)
    return Response(txt, mimetype="text/plain")
