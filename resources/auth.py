from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
import os
from schemas import AuthSchema

blp = Blueprint("auth", __name__, description="Authentication")

# Admin credentials
ADMIN_EMAIL = "kacem@gmail.com"
# Password hash for: K_A%C/e\M@
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "scrypt:32768:8:1$oSSq2qB2eXBH2API$74de2cfdc782d66aea96b75e96937981b0245c7823dc2fe0724754bad6dbcecf188947f0236a43eda928b6e751cafbc0a868c27d22d9e0e11f47252802c06e95")

@blp.route("/login")
class Login(MethodView):
    @blp.arguments(AuthSchema)
    def post(self, user_data):
        email = user_data.get("email")
        password = user_data.get("password")
        
        if not email or not password:
            return {"message": "Email and password required"}, 400
        
        # Check credentials
        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, password):
            access_token = create_access_token(
                identity="admin",
                additional_claims={"role": "admin"}
            )
            return {"access_token": access_token}
        
        return {"message": "Invalid credentials"}, 401
