import os

from flask import Flask, jsonify, request
from flask_smorest import Api
from flask_migrate import Migrate
from flask_caching import Cache
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

from db import db
from cache import cache

from blueprints.user import blp as UserBlueprint
from blueprints.admin import blp as AdminBlueprint
from blueprints.index import blp as IndexBlueprint
from blueprints.db import blp as DBBlueprint
from blueprints.movies import blp as MovieBlueprint

import models


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["API_TITLE"] = "IMDB REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs/v1/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        os.getenv("DB_URL", "sqlite:///movies.db") or db_url or "sqlite:///movies.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "secret")

    app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE", "redis")
    app.config["CACHE_REDIS_HOST"] = os.getenv(
        "REDIS_HOST", "localhost"
    )  # Redis server host
    app.config["CACHE_REDIS_PORT"] = os.getenv("REDIS_PORT", 6379)  # Redis server port
    app.config["CACHE_REDIS_DB"] = (
        os.getenv("REDIS_DB", 0) or 0
    )  # Redis database number
    app.config["CACHE_REDIS_PASSWORD"] = (
        os.getenv("REDIS_PASSWORD") or None
    )  # Optional Redis password

    cache.init_app(app)
    protected_routes = ["/movies"]
    # JWT
    jwt = JWTManager(app)

    @app.before_request
    def only_admins():
        for route in protected_routes:
            if request.path.startswith(route) and request.method in [
                "POST",
                "PATCH",
                "DELETE",
            ]:

                @jwt_required()
                def check_admin():
                    current_user = get_jwt()
                    if "isAdmin" in current_user and current_user["isAdmin"]:
                        return None
                    else:
                        return (
                            jsonify(message="Access denied: Admin privileges required"),
                            403,
                        )

                res = check_admin()
                if res is not None:
                    return res

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    db.init_app(app)

    migrate = Migrate(app, db)
    api = Api(app)

    api.register_blueprint(IndexBlueprint)
    api.register_blueprint(DBBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(AdminBlueprint)
    api.register_blueprint(MovieBlueprint)

    return app


if __name__ == "__main__":
    create_app().run()
