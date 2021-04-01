from models.settings import db
from datetime import datetime
from flask import request

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    session_token = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    @classmethod
    def get_by_session(cls):
        session_token = request.cookies.get("session_token")
        if not session_token:
            return None

        user = db.query(User).filter_by(session_token=session_token).first()
        return user