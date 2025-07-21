import pytest

@pytest.mark.usefixtures("isolated_transactions")
class Testpurchases:
    def test_create_purchase_with_submission(self, auth_user_client, submission, purchase_data):
        response = auth_user_client.post("/purchases", json=purchase_data)
        assert response.status_code == 201

    # client has no points
    def test_create_purchase_no_submission(self, auth_user_client, purchase_data):
        response = auth_user_client.post("/purchases", json=purchase_data)
        assert response.status_code == 403

    def test_create_purchase_frozen_user(self, user, auth_user_client, auth_mod_client, purchase_data):
        auth_mod_client.post(f"/users/{user.id}/freeze")
        response = auth_user_client.post("/purchases", json=purchase_data)
        assert response.status_code == 403

    def test_get_purchase(self, auth_user_client, purchase):
        response = auth_user_client.get(f"/purchases/{purchase.id}")
        assert response.status_code == 200

    def test_get_purchase_all(self, auth_mod_client, purchase):
        response = auth_mod_client.get("/purchases")
        assert response.status_code == 200

    def test_update_purchase(self, auth_admin_client, purchase):
        update_purchase_data = {"quantity": 10}
        response = auth_admin_client.patch(f"/purchases/{purchase.id}", json=update_purchase_data)
        assert response.status_code == 200

    def test_update_purchase_invalid_data(self, auth_admin_client, purchase):
        update_purchase_data = {"data": "data"}
        response = auth_admin_client.patch(f"/purchases/{purchase.id}", json=update_purchase_data)
        assert response.status_code == 400

    def test_update_purchase_inadequate_access(self, auth_mod_client, purchase):
        update_purchase_data = {"quantity": 100}
        response = auth_mod_client.patch(f"/purchases/{purchase.id}", json=update_purchase_data)
        assert response.status_code == 403

    def test_delete_purchase(self, auth_admin_client, purchase):
        response = auth_admin_client.delete(f"/purchases/{purchase.id}")
        assert response.status_code == 200
