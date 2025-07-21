import pytest


@pytest.mark.usefixtures("isolated_transactions")
class TestOther:
    def test_home(self, unauth_client):
        response = unauth_client.get("/")
        assert response.status_code == 200

    def test_login_user(self, unauth_client, user, password):
        login_data = {"username": user.username, "password": password}
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 200

    def test_login_moderator(self, unauth_client, moderator, password):
        login_data = {"username": moderator.username, "password": password}
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 200

    def test_login_admin(self, unauth_client, admin, password):
        login_data = {"username": admin.username, "password": password}
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 200

    def test_login_user_email(self, unauth_client, user, password):
        login_data = {"email": user.email, "password": password}
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 200

    def test_login_user_username_and_email(self, unauth_client, user, password):
        login_data = {
            "username": user.username,
            "email": user.email,
            "password": password,
        }
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 400

    def test_login_invalid_data(self, unauth_client):
        login_data = {"name": "name", "secret": "secret"}
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 400

    def test_login_invalid_password(self, unauth_client, user):
        login_data = {"username": user.username, "password": "____"}
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 401

    def test_login_nonexistant_username(self, unauth_client, password):
        login_data = {"username": "N/A", "password": password}
        response = unauth_client.post("/login", json=login_data)
        assert response.status_code == 401
