from app.api_client import get_user


def test_get_user_success():

    response = get_user(1)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert "username" in data