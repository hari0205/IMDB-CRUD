from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256

from data.data import load_sample_data, clear_data


blp = Blueprint("Database", __name__, description="Database related helpers")


@blp.route("/load", methods=["POST"])
class DbDataCreate(MethodView):
    @blp.response(200)
    def post(self):
        """Load sample data from from JSON file"""
        load_sample_data()
        return "Load success", 200


"""
Clear data from from DB
"""


@blp.route("/clear", methods=["POST"])
class dbDataClear(MethodView):
    @blp.response(200)
    def post(self):
        """Clear all data from database. Does not drop tables."""
        clear_data()
        return "Clear success", 200
