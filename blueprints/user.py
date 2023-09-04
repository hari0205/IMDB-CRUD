import uuid
from datetime import timedelta
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from passlib.hash import pbkdf2_sha256

from db import db


from schema import (
    AboutMeResponseSchema,
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
        409,
        ErrorResponseSchema,
        description="User registration failed. Duplicate entry",
    )
    @blp.response(500, ErrorResponseSchema, description="Unexpected Error")
    @blp.response(
        201, RegisterResponseSchema, description="User registration successful"
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
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print("Error: Unexpected Exception occurred ", e)
            abort(500, message="Unexpected error occured")

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
                identity={"email": user.email, "id": user.id},
                fresh=True,
                expires_delta=timedelta(hours=1),
            )
            return {"access_token": access_token, "message": "Login successful."}

        abort(401, message="Invalid credentials.")


@blp.route("/me", methods=["GET"])
class AboutMe(MethodView):
    @jwt_required()
    @blp.response(401, ErrorResponseSchema, description="Invalid credentials")
    @blp.response(200, AboutMeResponseSchema, description="Profile information of user")
    def get(self):
        user = get_jwt_identity()
        me = UserModel.query.get_or_404(user["id"])
        return AboutMeResponseSchema().dump(me)
