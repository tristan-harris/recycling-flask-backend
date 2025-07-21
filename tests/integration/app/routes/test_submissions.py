import pytest


@pytest.mark.usefixtures("isolated_transactions")
class TestSubmissions:
    def test_create_submission(self, auth_user_client, submission_post_data):
        response = auth_user_client.post("/submissions", json=submission_post_data)
        assert response.status_code == 201

    def test_create_submission_too_far(self, auth_user_client, submission_post_data):
        submission_post_data["latitude"] += 10
        submission_post_data["longitude"] += 10
        response = auth_user_client.post("/submissions", json=submission_post_data)
        assert response.status_code == 403

    def test_create_submission_frozen_user(
        self, user, auth_user_client, auth_mod_client, submission_post_data
    ):
        auth_mod_client.post(f"/users/{user.id}/freeze")
        response = auth_user_client.post("/submissions", json=submission_post_data)
        assert response.status_code == 403

    def test_get_submission(self, auth_mod_client, submission):
        response = auth_mod_client.get(f"/submissions/{submission.id}")
        assert response.status_code == 200

    def test_get_submission_all(self, auth_mod_client, submission):
        response = auth_mod_client.get("/submissions")
        assert response.status_code == 200

    def test_update_submission(self, auth_mod_client, submission):
        update_submission_data = {"status": "confirmed"}
        response = auth_mod_client.patch(
            f"/submissions/{submission.id}", json=update_submission_data
        )
        assert response.status_code == 200

    def test_update_submission_inadequate_access(self, auth_user_client, submission):
        update_submission_data = {"status": "confirmed"}
        response = auth_user_client.patch(
            f"/submissions/{submission.id}", json=update_submission_data
        )
        assert response.status_code == 403

    def test_update_submission_invalid_data(self, auth_admin_client, submission):
        update_submission_data = {"data": "data"}
        response = auth_admin_client.patch(
            f"/submissions/{submission.id}", json=update_submission_data
        )
        assert response.status_code == 400

    def test_delete_submission(self, auth_mod_client, submission):
        response = auth_mod_client.delete(f"/submissions/{submission.id}")
        assert response.status_code == 200
