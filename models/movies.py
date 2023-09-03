from sqlalchemy import Index
from db import db, movie_genre_association, favorites_association
from models.user import UserModel


# class MovieModel(db.Model):
#     __tablename__ = "movies"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     director = db.Column(db.String, nullable=False)
#     imdb_score = db.Column(db.Float(precision=1), nullable=False)
#     _99popularity = db.Column(db.Float(precision=1), nullable=False)

#     # Define a one-to-many relationship from movies to genres
#     genres = db.relationship("GenreModel", back_populates="movie")


class MovieModel(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    director = db.Column(db.String, nullable=False)
    imdb_score = db.Column(db.Float(precision=1), nullable=False)
    _99popularity = db.Column(db.Float(precision=1), nullable=False)

    # Define the many-to-many relationship with Genre
    genres = db.relationship(
        "GenreModel", secondary=movie_genre_association, back_populates="movies"
    )

    favourited_by = db.relationship(
        "UserModel",
        secondary=favorites_association,
        back_populates="favourite_movies",
    )


movie_idx = Index("movie_index", MovieModel.id, MovieModel.name, unique=True)
