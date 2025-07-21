import pytest

@pytest.mark.usefixtures("isolated_transactions")
class TestUsers:
    def test_create_user(self, unauth_client, user_data):
        response = unauth_client.post("/register", json=user_data)
        assert response.status_code == 201

    # username field must be unique
    def test_create_user_duplicate_user(self, unauth_client, user_data, user):
        user_data["email"] = "SomeOtherEmailAddress@mail.com"
        response = unauth_client.post("/register", json=user_data)
        assert response.status_code == 409 # conflict error

    # email field must be unique
    def test_create_user_duplicate_email(self, unauth_client, user_data, user):
        user_data["username"] = "SomeOtherUsername"
        response = unauth_client.post("/register", json=user_data)
        assert response.status_code == 409 # conflict error

    # # date of birth must use ISO 8601 standard (YYYY-MM-DD)
    # def test_create_user_invalid_dob_format(self, unauth_client, user_data):
    #     user_data["date_of_birth"] = "1/4/1990"
    #     response = unauth_client.post("/register", json=user_data)
    #     assert response.status_code == 400

    def test_create_user_too_young(self, unauth_client, user_data):
        # user_data["date_of_birth"] = "2024-01-01"
        user_data["age"] = 10
        response = unauth_client.post("/register", json=user_data)
        assert response.status_code == 403

    def test_get_user(self, auth_user_client, user):
        response = auth_user_client.get(f"/users/{user.id}")
        assert response.status_code == 200

    def test_get_user_invalid_token(self, auth_user_client, user):
        auth_user_client.environ_base["HTTP_AUTHORIZATION"] = "Bearer 1234"
        response = auth_user_client.get(f"/users/{user.id}")
        assert response.status_code == 422 # unprocessable content

    def test_get_user_all(self, auth_mod_client, user):
        response = auth_mod_client.get("/users")
        assert response.status_code == 200

    def test_get_user_all_inadequate_access(self, auth_user_client):
        response = auth_user_client.get("/users")
        assert response.status_code == 403

    def test_get_user_submissions(self, auth_user_client, user, submission):
        response = auth_user_client.get(f"/users/{user.id}/submissions")
        assert response.status_code == 200

    def test_get_user_purchases(self, auth_user_client, user, purchase):
        response = auth_user_client.get(f"/users/{user.id}/purchases")
        assert response.status_code == 200

    def test_get_user_balance(self, auth_user_client, user):
        response = auth_user_client.get(f"/users/{user.id}/balance")
        assert response.status_code == 200

    def test_update_user(self, auth_user_client, user):
        update_data = {"email": "users-new-email@mail.com"}
        response = auth_user_client.patch(f"/users/{user.id}", json=update_data)
        assert response.status_code == 200

    def test_update_user_password(self, auth_user_client, user):
        update_data = {"password": "new-password"}
        response = auth_user_client.patch(f"/users/{user.id}", json=update_data)
        assert response.status_code == 200

    def test_freeze_user(self, auth_mod_client, user):
        response = auth_mod_client.post(f"/users/{user.id}/freeze")
        assert response.status_code == 200

    def test_freeze_user_inadequate_access(self, auth_user_client, user):
        response = auth_user_client.post(f"/users/{user.id}/freeze")
        assert response.status_code == 403

    def test_freeze_user_attempt_staff(self, auth_mod_client, moderator):
        response = auth_mod_client.post(f"/users/{moderator.id}/freeze")
        assert response.status_code == 403

    def test_unfreeze_user(self, auth_mod_client, user):
        response = auth_mod_client.post(f"/users/{user.id}/unfreeze")
        assert response.status_code == 200

    def test_delete_user(self, auth_user_client, user):
        response = auth_user_client.delete(f"/users/{user.id}")
        assert response.status_code == 200
