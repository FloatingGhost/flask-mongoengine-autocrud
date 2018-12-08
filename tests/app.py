from flask import Flask
from flask_mongoengine_autocrud import create_crud
from tests.models.user import UserModel

app = Flask(__name__)


user_route = create_crud(
    UserModel,
    "users",
    "users"
)

app.register_blueprint(user_route, url_prefix="/user")
