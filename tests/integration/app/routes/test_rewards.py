import pytest

@pytest.mark.usefixtures("isolated_transactions")
class TestRewards:
    def test_create_reward(self, auth_admin_client, reward_data):
        response = auth_admin_client.post("/rewards", json=reward_data)
        assert response.status_code == 201

    def test_upload_reward_image(self, auth_admin_client, reward, reward_image_file_path):
        with open(reward_image_file_path, "rb") as image_file:
            response = auth_admin_client.post(f"/rewards/{reward.id}/image", data={"image": image_file})
        assert response.status_code == 200

    def test_upload_reward_image_inadequate_access(self, auth_mod_client, reward, reward_image_file_path):
        with open(reward_image_file_path, "rb") as image_file:
            response = auth_mod_client.post(f"/rewards/{reward.id}/image", data={"image": image_file})
        assert response.status_code == 403

    def test_upload_reward_image_invalid_data(self, auth_admin_client, reward):
        response = auth_admin_client.post(f"/rewards/{reward.id}/image", data={"image": "data"})
        assert response.status_code == 400

    def test_get_reward(self, unauth_client, reward):
        response = unauth_client.get(f"/rewards/{reward.id}")
        assert response.status_code == 200

    def test_get_reward_all(self, unauth_client, reward):
        response = unauth_client.get("/rewards")
        assert response.status_code == 200

    def test_update_reward(self, auth_admin_client, reward):
        update_reward_data = {"description": "New description"}
        response = auth_admin_client.patch(f"/rewards/{reward.id}", json=update_reward_data)
        assert response.status_code == 200

    def test_update_reward_cost(self, auth_admin_client, reward):
        update_reward_data = {"price": 1}
        response = auth_admin_client.patch(f"/rewards/{reward.id}", json=update_reward_data)
        assert response.status_code == 200

    def test_update_reward_invalid_data(self, auth_admin_client, reward):
        update_reward_data = {"data": "data"}
        response = auth_admin_client.patch(f"/rewards/{reward.id}", json=update_reward_data)
        assert response.status_code == 400

    def test_update_reward_inadequate_access(self, auth_mod_client, reward):
        update_reward_data = {"description": "New description"}
        response = auth_mod_client.patch(f"/rewards/{reward.id}", json=update_reward_data)
        assert response.status_code == 403

    def test_delete_reward(self, auth_admin_client, reward):
        response = auth_admin_client.delete(f"/rewards/{reward.id}")
        assert response.status_code == 200
