import pytest


@pytest.mark.usefixtures("isolated_transactions")
class TestLogs:
    def test_create_user_logs(self, unauth_client, auth_admin_client, user_data):
        unauth_client.post("/users", json=user_data)
        response = auth_admin_client.get("/logs/actions")
        assert response.status_code == 200

    def test_create_user_log(self, unauth_client, auth_admin_client, user_data):
        unauth_client.post("/users", json=user_data)
        response = auth_admin_client.get("/logs/actions")
        first_log_id = response.get_json()["user_action_logs"][0]["id"]
        response = auth_admin_client.get(f"/logs/actions/{first_log_id}")
        assert response.status_code == 200

    def test_create_bin_log(self, auth_admin_client, bin_data):
        auth_admin_client.post("/bins", json=bin_data)
        response = auth_admin_client.get("/logs/actions")
        assert response.status_code == 200

    def test_create_bin_log_inadequate_access(
        self, auth_admin_client, auth_mod_client, bin_data
    ):
        auth_admin_client.post("/bins", json=bin_data)
        response = auth_mod_client.get("/logs/actions")
        assert response.status_code == 403

    def test_update_bin_log(self, auth_admin_client, bin):
        auth_admin_client.patch(
            f"/bins/{bin.id}", json={"description": "New description"}
        )
        response = auth_admin_client.get("logs/actions")
        assert response.status_code == 200

    def test_update_reward_log(self, auth_admin_client, reward):
        auth_admin_client.patch(f"/rewards/{reward.id}", json={"price": 1})
        response = auth_admin_client.get("logs/actions")
        assert response.status_code == 200

    def test_delete_bin_log(self, auth_admin_client, bin):
        auth_admin_client.delete(f"/bins/{bin.id}")
        response = auth_admin_client.get("logs/actions")
        assert response.status_code == 200

    def test_delete_submission_log(self, auth_admin_client, submission):
        auth_admin_client.delete(f"/submissions/{submission.id}")
        response = auth_admin_client.get("logs/actions")
        assert response.status_code == 200
