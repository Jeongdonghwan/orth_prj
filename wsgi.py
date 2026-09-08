"""gunicorn 진입점: gunicorn -w 2 -b 0.0.0.0:PORT wsgi:app"""
from app import create_app

app = create_app()
