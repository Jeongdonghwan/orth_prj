"""로컬 개발 실행: python run.py  → http://127.0.0.1:5000"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=app.config.get("DEBUG", False))
