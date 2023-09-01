from db import db
from models.base import BaseModel


class AdminModel(BaseModel):
    __tablename__ = "admin"

    is_admin = db.Column(db.Boolean, default=True)
