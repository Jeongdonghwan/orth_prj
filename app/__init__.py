import json
import logging
from datetime import datetime

from flask import Flask, render_template

from config import Config
from .models import db

log = logging.getLogger(__name__)


def create_app(config_object=Config):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_object)

    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            app.config["DB_OK"] = True
        except Exception as e:  # DB 없어도 사이트는 떠야 한다
            app.config["DB_OK"] = False
            log.warning("DB 연결 실패 — 문의 저장 비활성: %s", e)

    from .routes import bp as pages_bp
    from .api import bp as api_bp
    from .admin import bp as admin_bp
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        c = app.config["CLINIC"]
        lat, lng = c.get("lat"), c.get("lng")
        if lat is not None and lng is not None:
            map_link = "https://map.kakao.com/link/to/{},{},{}".format(c["name"], lat, lng)
        else:
            map_link = "https://map.kakao.com/link/search/" + c["name"]
        def jsonld_clinic():
            data = {
                "@context": "https://schema.org",
                "@type": "MedicalClinic",
                "name": c["name"],
                "url": app.config.get("SITE_URL", ""),
                "telephone": c["tel_link"],
                "medicalSpecialty": "Anesthesia",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": c["address_road"],
                    "addressLocality": c["city"],
                    "postalCode": c.get("postal", ""),
                    "addressCountry": "KR",
                },
                "openingHoursSpecification": [
                    {"@type": "OpeningHoursSpecification", "dayOfWeek": o["days"],
                     "opens": o["opens"], "closes": o["closes"]}
                    for o in c["opening_hours"]
                ],
            }
            if lat is not None and lng is not None:
                data["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}
            return json.dumps(data, ensure_ascii=False)

        return {
            "clinic": c,
            "jsonld_clinic": jsonld_clinic,
            "map_link": map_link,
            "kakao_js_key": app.config.get("KAKAO_JS_KEY", ""),
            "naver_site_verification": app.config.get("NAVER_SITE_VERIFICATION", ""),
            "site_url": app.config.get("SITE_URL", ""),
            "year": datetime.now().year,
        }

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("404.html"), 404

    return app
