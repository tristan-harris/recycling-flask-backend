import pytest

@pytest.mark.usefixtures("isolated_transactions")
class TestStaff:
    def test_create_staff(self, auth_admin_client, staff_data):
        response = auth_admin_client.post("/staff", json=staff_data)
        assert response.status_code == 201

    def test_create_staff_inadequate_access(self, auth_mod_client, staff_data):
        response = auth_mod_client.post("/staff", json=staff_data)
        assert response.status_code == 403

    def test_create_staff_invalid_data(self, auth_admin_client, staff_data):
        staff_data["role"] = "N/A"
        response = auth_admin_client.post("/staff", json=staff_data)
        assert response.status_code == 400

    def test_get_staff(self, auth_mod_client, staff):
        response = auth_mod_client.get(f"/staff/{staff.user_id}")
        assert response.status_code == 200

    def test_get_staff_inadequate_access(self, auth_user_client, admin):
        response = auth_user_client.get(f"/staff/{admin.id}")
        assert response.status_code == 403

    def test_get_staff_all(self, auth_mod_client, staff):
        response = auth_mod_client.get("/staff")
        assert response.status_code == 200

    def test_get_staff_all_inadequate_access(self, auth_user_client):
        response = auth_user_client.get("/staff")
        assert response.status_code == 403

    def test_update_staff(self, auth_admin_client, staff):
        update_staff_data = {"role": "moderator"}
        response = auth_admin_client.patch(f"/staff/{staff.user_id}", json=update_staff_data)
        assert response.status_code == 200

    def test_update_staff_inadequate_access(self, auth_mod_client, admin):
        update_staff_data = {"role": "administrator"}
        response = auth_mod_client.patch(f"/staff/{admin.id}", json=update_staff_data)
        assert response.status_code == 403

    def test_update_staff_invalid_data(self, auth_admin_client, staff):
        update_staff_data = {"data": "data"}
        response = auth_admin_client.patch(f"/staff/{staff.user_id}", json=update_staff_data)
        assert response.status_code == 400

    def test_delete_staff(self, auth_admin_client, staff):
        response = auth_admin_client.delete(f"/staff/{staff.user_id}")
        assert response.status_code == 200

    def test_delete_staff_inadequate_access(self, auth_mod_client, staff):
        response = auth_mod_client.delete(f"/staff/{staff.user_id}")
        assert response.status_code == 403
