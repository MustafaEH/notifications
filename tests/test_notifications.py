

def test_get_notifications_without_token(client):
    response = client.get("/notifications/")
    assert response.status_code == 401


def test_create_valid_notification(auth_client):
    response = auth_client.post("/notifications/", json={
        "recipient": "test@gmail.com",
        "subject": "Test",
        "channel": "email",
        "content": "Hello"
    })
    assert response.status_code == 201

def test_create_invalid_notification(auth_client):
    response = auth_client.post("/notifications/", json={"title": "Test Notification"})
    assert response.status_code == 422

def test_get_notifications_authorized(auth_client):
    response = auth_client.get("/notifications/")
    assert response.status_code == 200

def test_get_notification_by_id(auth_client):
    # create first
    create = auth_client.post("/notifications/", json={
        "recipient": "test@gmail.com",
        "subject": "Test",
        "channel": "email",
        "content": "Hello"
    })
    notification_id = create.json()["id"]
    # then get by id
    response = auth_client.get(f"/notifications/{notification_id}")
    assert response.status_code == 200

def test_delete_notification(auth_client):
    # create first
    create = auth_client.post("/notifications/", json={
        "recipient": "test@gmail.com",
        "subject": "Test",
        "channel": "email",
        "content": "Hello"
    })
    notification_id = create.json()["id"]
    # then delete
    response = auth_client.delete(f"/notifications/{notification_id}")
    assert response.status_code == 204

