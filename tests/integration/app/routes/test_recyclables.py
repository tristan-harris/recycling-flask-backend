import pytest


@pytest.mark.usefixtures("isolated_transactions")
class TestRecyclables:
    def test_create_recyclable(self, auth_admin_client, recyclable_data):
        response = auth_admin_client.post("/recyclables", json=recyclable_data)
        assert response.status_code == 201

    def test_get_recyclable(self, unauth_client, recyclable):
        response = unauth_client.get(f"/recyclables/{recyclable.id}")
        assert response.status_code == 200

    def test_get_recyclable_all(self, unauth_client, recyclable):
        response = unauth_client.get("/recyclables")
        assert response.status_code == 200

    def test_update_recyclable(self, auth_admin_client, recyclable):
        update_recyclable_data = {"description": "New description"}
        response = auth_admin_client.patch(
            f"/recyclables/{recyclable.id}", json=update_recyclable_data
        )
        assert response.status_code == 200

    def test_delete_recyclable(self, auth_admin_client, recyclable):
        response = auth_admin_client.delete(f"/recyclables/{recyclable.id}")
        assert response.status_code == 200
