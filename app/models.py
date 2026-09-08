from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Inquiry(db.Model):
    __tablename__ = "inquiries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    part = db.Column(db.String(20))
    message = db.Column(db.Text)
    ip = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_read = db.Column(db.Boolean, default=False)

    def to_row(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "part": self.part or "",
            "message": self.message or "",
            "ip": self.ip or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
            "is_read": int(bool(self.is_read)),
        }
