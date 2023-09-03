from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# Table association for Movies and Genres
movie_genre_association = db.Table(
    "movie_genre_association",
    db.Column("movie_id", db.Integer, db.ForeignKey("movie.id")),
    db.Column("genre_id", db.Integer, db.ForeignKey("genre.id")),
)

# Table association for Favorites and Movies
favorites_association = db.Table(
    "user_favorite_movies",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("movie_id", db.Integer, db.ForeignKey("movie.id")),
)
