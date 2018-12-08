import pytest
from pymongo import MongoClient
from tests.app import app
from mongoengine import connect as me_connect


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    cli = MongoClient()
    cli.drop_database("Cruddify")
    me_connect("Cruddify")
    yield client
