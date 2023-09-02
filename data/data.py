import json
from sqlalchemy.exc import SQLAlchemyError


from db import db
from models import MovieModel, GenreModel

"""
For 1-to-Many relationship. 
"""
# def load_sample_data():
#     try:
#         with open("data/imdb.json", "r") as json_file:
#             json_data = json.load(json_file)

#             for item in json_data:
#                 # Create a new movie entry
#                 movie = MovieModel(
#                     name=item["name"],
#                     director=item["director"],
#                     imdb_score=item["imdb_score"],
#                     _99popularity=item["99popularity"],
#                 )

#                 # Create a list to hold genre objects for this movie
#                 genres_for_movie = []

#                 for genre_name in item["genre"]:
#                     # If it doesn't exist, create a new genre object
#                     genre = GenreModel(name=genre_name)
#                     db.session.add(genre)
#                     genres_for_movie.append(genre)

#                 # Set the genres attribute for the movie to establish the association
#                 movie.genres = genres_for_movie

#                 # Atomic transactions to add movie entries to the database
#                 db.session.add(movie)

#             db.session.commit()

#             print("Sample data loaded successfully")

#     except FileNotFoundError:
#         print("Sample data file not found")
#     except Exception as e:
#         print(f"Error loading sample data: {e}")


def load_sample_data() -> None:
    """
    Load the sample data provided.


    """
    try:
        with open("data/imdb.json", "r") as json_file:
            json_data: list = json.load(json_file)

            for item in json_data:
                # Create a new movie entry
                movie = MovieModel(
                    name=item["name"],
                    director=item["director"],
                    imdb_score=item["imdb_score"],
                    _99popularity=item["99popularity"],
                )

                # Create a list to hold genre objects for this movie
                genres_for_movie = []

                for genre_name in item["genre"]:
                    # Check if the genre with this name already exists in the database
                    existing_genre = GenreModel.query.filter_by(
                        name=genre_name.strip()
                    ).first()

                    if existing_genre:
                        genres_for_movie.append(existing_genre)
                    else:
                        # If it doesn't exist, create a new genre object
                        genre = GenreModel(name=genre_name.strip())
                        db.session.add(genre)
                        genres_for_movie.append(genre)
                        db.session.commit()

                # Set the genres attribute for the movie to establish the association
                movie.genres = genres_for_movie

                # Atomic transactions to add movie entries to the database
                db.session.add(movie)

            db.session.commit()

            print("Sample data loaded successfully")

    except FileNotFoundError:
        print("Sample data file not found")
    except SQLAlchemyError as err:
        print("SQL ERROR: %s", err)
    except Exception as e:
        print(f"Error loading sample data: {e}")


def clear_data() -> None:
    """Clears the DB data. Does not clear tables."""
    meta = db.metadata

    # Avoid foreign key violation
    # Clears childrens|Associations before parents
    try:
        for table in reversed(meta.sorted_tables):
            print("Clear table: ", table)
            db.session.execute(table.delete())
        db.session.commit()
    except Exception as e:
        print(f"Error occured clearing tables: {e}")
