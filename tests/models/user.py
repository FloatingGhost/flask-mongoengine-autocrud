from mongoengine import Document
from mongoengine.fields import (StringField, BooleanField)


class UserModel(Document):
    meta = {"collection": "Users"}
    username = StringField(required=True, unique=True)
    is_admin = BooleanField(default=False)
    email = StringField(default="")
