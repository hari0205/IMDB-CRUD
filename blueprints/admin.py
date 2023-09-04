from flask import request
from datetime import timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256

from db import db


from schema import (
    AdminLoginSchema,
    AdminSchema,
    LoginAdminResponseSchema,
    RegisterAdminResponseSchema,
    ErrorResponseSchema,
)
from models import AdminModel


blp = Blueprint(
    "Admin", __name__, description="Operations on admin", url_prefix="/admin"
)


@blp.route("/register")
class UserRegistration(MethodView):
    @blp.arguments(AdminSchema)
    @blp.response(409, ErrorResponseSchema, description="Admin already registered")
    @blp.response(500, ErrorResponseSchema, description="Unexpected error")
    @blp.response(201, description="Admin created", schema=RegisterAdminResponseSchema)
    def post(self, user_data):
        """Create a new admin user

        Args:
            AdminLoginInfo: Email and password of the admin user

        Returns:
            string : Status indicating success or failure
        """
        if AdminModel.query.filter(AdminModel.email == user_data["email"]).first():
            abort(409, message="A user with that username already exists.")

        admin_user = AdminModel(
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            is_admin=True,
        )
        try:
            db.session.add(admin_user)
            db.session.commit()
        except Exception as e:
            print("Unexpected exception occured", e)
            abort(500, message="Unexpected Exception occurred")

        return {"message": "Admin created successfully."}, 201


@blp.route("/login", methods=["POST"])
class UserLogin(MethodView):
    @blp.arguments(AdminLoginSchema)
    @blp.response(400, ErrorResponseSchema, description="Login failed. Bad credentials")
    @blp.response(200, LoginAdminResponseSchema)
    def post(self, user_data):
        """Route for authenticating an admin user

        Args:
            AdminLoginData : email and password of the admin user

        Returns:
            string: Access token for the admin user
        """
        user = AdminModel.query.filter(AdminModel.email == user_data["email"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(
                identity=user.email,
                fresh=True,
                expires_delta=timedelta(hours=1),
                additional_claims={"isAdmin": True},
            )
            return {"access_token": access_token, "message": "Login successful."}

        abort(401, message="Invalid credentials.")
