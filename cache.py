from flask_caching import Cache
from flask import request

cache = Cache()


def custom_movie_key_generator():
    name = request.view_args["name"]

    return f"movie#{name}"
