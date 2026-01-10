from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import os

blp = Blueprint("auth", __name__, description="Authentication")


@blp.route("/login")
class Login(MethodView):
    def post(self):
        data = request.get_json(force=True)
        username = data.get("username")
        password = data.get("password")

        # Admin credentials
        admin_user = os.environ.get("ADMIN_USERNAME", "admin")
        admin_pass = os.environ.get("ADMIN_PASSWORD", "password")
        
        # Dept chef credentials
        chef_user = os.environ.get("CHEF_USERNAME", "chef")
        chef_pass = os.environ.get("CHEF_PASSWORD", "chef123")

        if username == admin_user and password == admin_pass:
            access_token = create_access_token(
                identity=username,
                additional_claims={"role": "admin"}
            )
            return {"access_token": access_token, "role": "admin"}
        
        if username == chef_user and password == chef_pass:
            access_token = create_access_token(
                identity=username,
                additional_claims={"role": "dept_chef"}
            )
            return {"access_token": access_token, "role": "dept_chef"}

        return {"message": "Bad credentials"}, 401


@blp.route("/protected")
class Protected(MethodView):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role", "student")
        return {"logged_in_as": current_user, "role": role}