from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_

from db import db
from cache import cache, custom_movie_key_generator

from schema import (
    MovieResponseSchema,
    CreateMoviesSchema,
    UpdateMoviesSchema,
    ErrorResponseSchema,
    DeleteResponseSchema,
    PaginatedResponseSchema,
)
from models import MovieModel, GenreModel, UserModel


blp = Blueprint(
    "Movies", __name__, description="Operations on Movies", url_prefix="/movies"
)


@blp.route("/", methods=["GET", "POST"])
class Movies(MethodView):
    @blp.response(404, ErrorResponseSchema, description="No movies were found")
    @cache.cached(timeout=10)  # Change timeout later or set explicitly
    @blp.response(200, PaginatedResponseSchema, description="List of all movies")
    def get(self):
        """Gets all movies in the database

        Returns:
            Movies: All movies in the database
        """

        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=25, type=int)
        movies = MovieModel.query.options(db.joinedload(MovieModel.genres)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        if not movies:
            abort(404, message="No movies found in the database.")

        serialized_movies = MovieResponseSchema(many=True).dump(movies)
        res_data = {
            "page": movies.page,
            "per_page": movies.per_page,
            "total": movies.total,
            "movies": serialized_movies,  # Include the list of movies in the response
        }
        serialized_data = PaginatedResponseSchema().dump(res_data)
        return serialized_data

    @jwt_required()
    @blp.arguments(CreateMoviesSchema)
    @blp.response(
        403, ErrorResponseSchema, description="No privileges to create new movies"
    )
    @blp.response(400, ErrorResponseSchema, description="Bad Input")
    @blp.response(500, ErrorResponseSchema, description="Unexpected errror")
    @blp.response(201, MovieResponseSchema, description="New movie created.")
    def post(self, movie_data):
        """Creates a new movie

        Args:
            movie_data (CreateMovieSchema): Name, director, score ,popularity and genres for a movie

        Returns:
            Movie: Newly created movie
        """
        movie = MovieModel(
            name=movie_data["name"],
            director=movie_data["director"],
            imdb_score=movie_data["imdb_score"],
            _99popularity=movie_data["_99popularity"],
        )

        genres_for_movie = []
        for genre_name in movie_data["genres"]:
            # Check if the genre with this name already exists in the database
            existing_genre = GenreModel.query.filter_by(name=genre_name.strip()).first()

            if existing_genre:
                genres_for_movie.append(existing_genre)
            else:
                # If it doesn't exist, create a new genre object
                genre = GenreModel(name=genre_name.strip())
                db.session.add(genre)
                genres_for_movie.append(genre)

        movie.genres.extend(genres_for_movie)
        try:
            db.session.add(movie)
            db.session.commit()
        except Exception as e:
            print("Error: Unexpected error occurred ", e)
            db.session.rollback()
            abort(500, message="Unexpected error occurred ")

        serialized_movie = MovieResponseSchema().dump(movie)
        cache.clear()
        return serialized_movie, 201


@blp.route("<string:name>", methods=["GET", "PATCH", "DELETE"])
class FetchMovieByName(MethodView):
    @blp.response(404, ErrorResponseSchema, description="Movie not found")
    @blp.response(200, MovieResponseSchema, description="Movie with given name.")
    def get(self, name):
        """Get a movie by name

        Args:
            name (string): Name of the movie to fetch

        Returns:
            MovieSchema: Movie with the given name.
        """
        movie = (
            MovieModel.query.filter_by(name=name)
            .options(db.joinedload(MovieModel.genres))
            .first()
        )

        if not movie:
            abort(404, message=f"Movie with name {name} not found")

        cache.set(f"movies#{name}", movie, timeout=10)
        return movie

    @jwt_required()
    @blp.arguments(UpdateMoviesSchema)
    @blp.response(
        403, ErrorResponseSchema, description="No privileges to update movies"
    )
    @blp.response(404, ErrorResponseSchema, description="Movie not found")
    @blp.response(500, ErrorResponseSchema, description="Unexpected error")
    @blp.response(200, MovieResponseSchema, description="Updated movie")
    def patch(self, update_data, name):
        """Update movie details

        Args:
            update_data (UpdateMovieSchema): Fields to update
            name (string): Name of the movie to update

        Returns:
            MovieResponseSchema: Updated movie
        """
        movie = (
            MovieModel.query.filter_by(name=name)
            .options(db.joinedload(MovieModel.genres))
            .first()
        )

        if not movie:
            abort(404, f"Moive {name} not found")
        else:
            # Update the movie attributes
            movie.name = update_data.get("name", movie.name)
            movie.director = update_data.get("director", movie.director)
            movie.imdb_score = update_data.get("imdb_score", movie.imdb_score)
            movie._99popularity = update_data.get("_99popularity", movie._99popularity)

        if "genres" in update_data:
            # Clear existing genres
            movie.genres = []
            for genre_name in update_data["genres"]:
                genre = GenreModel.query.filter_by(name=genre_name.strip()).first()
                if genre:
                    movie.genres.append(genre)
                else:
                    # Create a new genre if it doesn't exist
                    new_genre = GenreModel(name=genre_name.strip())
                    db.session.add(new_genre)
                    movie.genres.append(new_genre)
            try:
                db.session.commit()
                db.session.refresh(movie)
            except Exception as e:
                print("Error: Unexpected error occurred ", e)
                db.session.rollback()
                abort(500, message="Unexpected error occurred ")
            cache.clear()
            return movie

    @jwt_required()
    @blp.response(404, ErrorResponseSchema, description="Movie not found.")
    @blp.response(500, ErrorResponseSchema, description="Unexpected Error")
    @blp.response(204, DeleteResponseSchema, description="Movie deleted successfully")
    def delete(self, name):
        """Delete a movie from the database

        Args:
            name (string): Name of the movie to delete

        Returns:
            string: message indicating success or error
        """
        movie = (
            MovieModel.query.filter_by(name=name)
            .options(db.joinedload(MovieModel.genres))
            .first()
        )

        if not movie:
            abort(404, f"Movie {name} not found")
        try:
            db.session.delete(movie)
            db.session.commit()
        except Exception as e:
            print("Error: Unexpected Error occurred")
            db.session.rollback()
            abort(500, message="Unexpected Error occurred")

        cache.clear()
        return {"message": "Item deleted."}


@blp.route("<int:id>", methods=["GET", "PATCH", "DELETE"])
class FetchMovieByID(MethodView):
    @blp.response(404, ErrorResponseSchema, description="Movie with ID not found")
    @blp.response(200, MovieResponseSchema, description="Movie response")
    def get(self, id):
        """Get movie based on ID

        Args:
            id (int): ID of the movie

        Returns:
            MovieResponseSchema: Response movie with given ID.
        """
        return MovieModel.query.get_or_404(id)

    @blp.arguments(UpdateMoviesSchema)
    @blp.response(404, ErrorResponseSchema, description="Movie with ID not found")
    @blp.response(500, ErrorResponseSchema, description="Unexpected error")
    @blp.response(200, MovieResponseSchema, description="Movie updated")
    @jwt_required()
    def patch(self, update_data, id):
        """Update a Movie

        Args:
            update_data (UpdateMovieSchema): Fields to update movie data
            id (Number): Id of the movie to update

        Returns:
            MovieResponseSchema: Returns updated movie.
        """
        movie = MovieModel.query.get_or_404(id)

        if movie:
            # Update the movie attributes
            movie.name = update_data.get("name", movie.name)
            movie.director = update_data.get("director", movie.director)
            movie.imdb_score = update_data.get("imdb_score", movie.imdb_score)
            movie._99popularity = update_data.get("_99popularity", movie._99popularity)

        if "genres" in update_data:
            # Clear existing genres
            movie.genres = []
            for genre_name in update_data["genres"]:
                genre = GenreModel.query.filter_by(name=genre_name.strip()).first()
                if genre:
                    movie.genres.append(genre)
                else:
                    # Create a new genre if it doesn't exist
                    new_genre = GenreModel(name=genre_name.strip())
                    db.session.add(new_genre)
                    movie.genres.append(new_genre)

        try:
            db.session.commit()
            db.session.refresh(movie)
        except Exception as e:
            print("Error: Unexpected exception occurred ", e)
            db.session.rollback()
            abort(500, message="Unexpected exception occurred")

        cache.clear()
        return movie

    @jwt_required()
    @blp.response(404, ErrorResponseSchema, description="Movie not found")
    @blp.response(500, ErrorResponseSchema, description="Unexpected error")
    @blp.response(204, DeleteResponseSchema, description="Movie deleted")
    def delete(self, id):
        """Delete a  movie from the database"""
        movie = MovieModel.query.get_or_404(id)
        try:
            db.session.delete(movie)
            db.session.commit()
        except Exception as e:
            print("Unexpected exception occurred ", e)
            db.session.rollback()
        cache.clear()
        return {"message": "Item deleted."}


@blp.route("/search", methods=["GET"])
class SearchMovies(MethodView):
    @blp.response(404, description="No matching criteria", schema=ErrorResponseSchema)
    @cache.cached(timeout=100)
    @blp.response(
        200,
        PaginatedResponseSchema,
        description="List of movies that match the search criteria.",
    )
    def get(self):
        """Get a list of movies that match the search criteria

        Returns:
            MovieResponseSchema: Result of search
        """
        name = request.args.get("name")
        director = request.args.get("director")
        min_rating = request.args.get("min_rating")
        maxscore = request.args.get("max_rating")
        popularity = request.args.get("popularity")
        genres = request.args.get("genres")

        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=25, type=int)

        if genres:
            genre = genres.split(",")

        query = MovieModel.query
        if name:
            query = query.filter(MovieModel.name.ilike(f"%{name}%"))
        if director:
            query = query.filter(MovieModel.director.ilike(f"%{director}%"))

        # Filter by IMDb score range (between min and max)
        if min_rating:
            query = query.filter(MovieModel.imdb_score >= float(min_rating))
        if maxscore:
            query = query.filter(MovieModel.imdb_score <= float(maxscore))

        if popularity:
            query = query.filter(MovieModel._99popularity == float(popularity))

        if genres:
            genre_conds = [MovieModel.genres.any(name=gen) for gen in genre] or []
            query = query.filter(or_(*genre_conds))

        # Execute the query and fetch the results
        movies = query.order_by(MovieModel._99popularity.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        if not movies or movies.total == 0:
            abort(404, "No movies with the criteria specified was found.")

        serialized_movies = MovieResponseSchema(many=True).dump(movies)
        res_data = {
            "page": movies.page,
            "per_page": movies.per_page,
            "total": movies.total,
            "movies": serialized_movies,  # Include the list of movies in the response
        }
        serialized_data = PaginatedResponseSchema().dump(res_data)
        return serialized_data


@blp.route("/<int:id>/favourite", methods=["POST"])
@blp.route("/<string:name>/favourite", methods=["DELETE"])
class FavoriteMovie(MethodView):
    @jwt_required()
    @blp.response(404, ErrorResponseSchema)
    @blp.response(200, MovieResponseSchema)
    def post(self, id):
        """Favourite a movie based on ID

        Args:
            id (int): ID of the movie

        Returns:
            MovieResponseSchema: Response movie favourited with given ID.
        """
        movie = MovieModel.query.get_or_404(id)
        user_creds = get_jwt_identity()

        user = UserModel.query.get_or_404(user_creds["id"])
        if movie not in user.favourite_movies:
            user.favourite_movies.append(movie)
        else:
            abort(400, message="Movie already in favourites.")

        db.session.add(user)
        db.session.commit()

        return MovieResponseSchema().dump(movie)

    @jwt_required()
    @blp.response(204, DeleteResponseSchema)
    def delete(self, name):
        """Delete a movie from favorites

        Args:
            name (string): Name of the movie to be deleted
        """
        name = str(name)
        user_creds = get_jwt_identity()
        user = UserModel.query.get_or_404(user_creds["id"])

        to_remove = list(
            filter(lambda movie: movie.name == name, user.favourite_movies)
        )

        if not to_remove:
            abort(404, message=f"Movie '{name}' not found in favorites")

        for movie in to_remove:
            user.favourite_movies.remove(movie)

        db.session.commit()
        return None, 204
