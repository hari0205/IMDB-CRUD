from db import db
from datetime import datetime
from sqlalchemy import Column, Integer, String


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String, nullable=False)

    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
