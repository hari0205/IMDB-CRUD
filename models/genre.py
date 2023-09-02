from db import db, movie_genre_association


# class GenreModel(db.Model):
#     __tablename__ = "genres"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)

#     # Define the foreign key relationship to movies
#     movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"))

#     # Define the back-reference from genres to movies
#     movie = db.relationship("MovieModel", back_populates="genres")


class GenreModel(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    # Many-to-many relationship with Movie
    movies = db.relationship(
        "MovieModel", secondary=movie_genre_association, back_populates="genres"
    )
