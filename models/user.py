from sqlalchemy import Index
from db import db, favorites_association
from models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    favourite_movies = db.relationship(
        "MovieModel",
        secondary=favorites_association,
        back_populates="favourited_by",
    )


user_idx = Index("user_index", UserModel.id, UserModel.name, unique=True)
