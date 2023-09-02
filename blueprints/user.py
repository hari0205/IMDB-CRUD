import uuid
from datetime import timedelta
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256

from db import db


from schema import (
    UserLoginSchema,
    UserSchema,
    LoginResponseSchema,
    RegisterResponseSchema,
    ErrorResponseSchema,
)
from models import UserModel


blp = Blueprint(
    "Users", __name__, description="Operations on users", url_prefix="/users"
)


@blp.route("/register", methods=["POST"])
class UserRegistration(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(
        201, RegisterResponseSchema, description="User registration successful"
    )
    @blp.response(
        409,
        RegisterResponseSchema,
        description="User registration failed. Duplicate entry",
    )
    def post(self, user_data):
        """Create a new user.

        Args:
            user_data (UserRegisterSchema): Email and Password of the User

        Returns:
            string: Status Indicating success or failure.
        """
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/login", methods=["POST"])
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.response(
        401, ErrorResponseSchema, description="User Login failure. Bad credentials"
    )
    @blp.response(
        200,
        LoginResponseSchema,
        description="User Login success.",
    )
    def post(self, user_data):
        """Login a user

        Args:
            user_data (UserLoginSchema): Email and password of a User

        Returns:
            string: Access token of the user.
        """
        user = UserModel.query.filter(UserModel.email == user_data["email"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(
                identity=user.email,
                fresh=True,
                expires_delta=timedelta(hours=1),
            )
            return {"access_token": access_token, "message": "Login successful."}

        abort(401, message="Invalid credentials.")
