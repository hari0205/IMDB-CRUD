from flask import Flask, jsonify, request
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from db import db

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
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///movies.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_SECRET_KEY"] = "secret"  # Replace later

    # JWT
    jwt = JWTManager(app)

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

    # @app.before_request
    # def jwt_middleware():
    #     if request.endpoint and request.endpoint in app.view_functions:
    #         # Check if the endpoint is in the list of protected endpoints
    #         if request.endpoint in protected_routes:
    #             # Get the JWT token from the Authorization header
    #             authorization_header = request.headers.get("Authorization", None)
    #             if authorization_header is None:
    #                 return jsonify(message="Authorization header is missing"), 401

    #             parts = authorization_header.split()
    #             if len(parts) != 2 or parts[0].lower() != "bearer":
    #                 return jsonify(message="Invalid token format"), 401

    #             token = parts[1]

    #             # Verify the JWT token
    #             try:
    #                 identity = jwt.decode_token(token)
    #                 setattr(request, "current_identity", identity)
    #             except Exception as e:
    #                 return jsonify(message="Token is invalid"), 401

    db.init_app(app)

    # migrate = Migrate(app, db)
    api = Api(app)

    ## Delete later
    with app.app_context():
        import models

        db.create_all()

    api.register_blueprint(IndexBlueprint)
    api.register_blueprint(DBBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(AdminBlueprint)
    api.register_blueprint(MovieBlueprint)

    return app
