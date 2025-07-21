import pytest


@pytest.mark.usefixtures("isolated_transactions")
class TestMotivations:
    def test_create_motivation(self, auth_user_client, motivation_data):
        response = auth_user_client.post("/motivations", json=motivation_data)
        assert response.status_code == 201

    def test_get_motivation(self, auth_mod_client, motivation):
        response = auth_mod_client.get(f"/motivations/{motivation.user_id}")
        assert response.status_code == 200

    def test_get_motivation_all(self, auth_mod_client, motivation):
        response = auth_mod_client.get("/motivations")
        assert response.status_code == 200

    def test_update_motivation(self, auth_admin_client, motivation):
        update_motivation_data = {"motivation": "New motivation text"}
        response = auth_admin_client.patch(
            f"/motivations/{motivation.user_id}", json=update_motivation_data
        )
        assert response.status_code == 200

    def test_update_motivation_inadequate_access(self, auth_mod_client, motivation):
        update_motivation_data = {"motivation": "New motivation text"}
        response = auth_mod_client.patch(
            f"/motivations/{motivation.user_id}", json=update_motivation_data
        )
        assert response.status_code == 403

    def test_update_motivation_invalid_data(self, auth_admin_client, motivation):
        update_motivation_data = {"data": "data"}
        response = auth_admin_client.patch(
            f"/motivations/{motivation.user_id}", json=update_motivation_data
        )
        assert response.status_code == 400

    def test_delete_motivation(self, auth_admin_client, motivation):
        response = auth_admin_client.delete(f"/motivations/{motivation.user_id}")
        assert response.status_code == 200
