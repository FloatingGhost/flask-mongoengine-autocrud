def test_valid_create(client):
    # First, try posting a valid user
    payload = {
        "username": "testuser"
    }
    req = client.post("/user/", json=payload)
    assert req.status_code == 201
    assert req.get_json()["username"] == "testuser"


def test_create_no_required_field(client):
    payload = {}
    req = client.post("/user/", json=payload)
    assert req.status_code == 400


def test_create_double_unique_field(client):
    payload = {
        "username": "testuser"
    }
    client.post("/user/", json=payload)
    req = client.post("/user/", json=payload)
    assert req.status_code == 500


def test_get_all(client):
    payload = {
        "username": "testuser"
    }
    client.post("/user/", json=payload)
    req = client.get("/user/")
    assert req.status_code == 200
    out = req.get_json()
    assert len(out) == 1
    assert out[0]["username"] == "testuser"


def test_get_one(client):
    payload = {
        "username": "testuser"
    }
    req = client.post("/user/", json=payload)
    created_id = req.get_json()["_id"]
    req = client.get("/user/{}".format(created_id))
    out = req.get_json()
    assert isinstance(out, dict)
    assert out["_id"] == created_id
