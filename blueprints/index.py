from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint("Index", __name__, description="HealthCheck route")


@blp.route("/")
class Index(MethodView):
    def get(self):
        """HealthCheck route

        Returns:
            statuscode: HTTP status code for the application
        """
        return {"message": "Hello, world!"}, 200
