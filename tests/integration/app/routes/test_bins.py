import pytest


@pytest.mark.usefixtures("isolated_transactions")
class TestBins:
    def test_create_bin(self, auth_admin_client, bin_data):
        response = auth_admin_client.post("/bins", json=bin_data)
        assert response.status_code == 201

    def test_upload_bin_image(self, auth_admin_client, bin, bin_image_file_path):
        with open(bin_image_file_path, "rb") as image_file:
            response = auth_admin_client.post(
                f"/bins/{bin.id}/image", data={"image": image_file}
            )
        assert response.status_code == 200

    def test_upload_bin_image_inadequate_access(
        self, auth_mod_client, bin, bin_image_file_path
    ):
        with open(bin_image_file_path, "rb") as image_file:
            response = auth_mod_client.post(
                f"/bins/{bin.id}/image", data={"image": image_file}
            )
        assert response.status_code == 403

    def test_upload_bin_image_invalid_data(self, auth_admin_client, bin):
        response = auth_admin_client.post(
            f"/bins/{bin.id}/image", data={"image": "data"}
        )
        assert response.status_code == 400

    def test_get_bin(self, unauth_client, bin):
        response = unauth_client.get(f"/bins/{bin.id}")
        assert response.status_code == 200

    def test_get_bin_all(self, unauth_client, bin):
        response = unauth_client.get("/bins")
        assert response.status_code == 200

    def test_get_bin_whithout_whitelist(self, unauth_client, bin):
        response = unauth_client.get(f"/bins/{bin.id}/whitelist")
        assert response.status_code == 200

    def test_get_bin_with_whitelist(self, unauth_client, bin_with_whitelist):
        response = unauth_client.get(f"/bins/{bin_with_whitelist.id}/whitelist")
        assert response.status_code == 200

    def test_get_bin_image(self, auth_admin_client, bin, bin_image_file_path):
        with open(bin_image_file_path, "rb") as image_file:
            auth_admin_client.post(f"/bins/{bin.id}/image", data={"image": image_file})
        response = auth_admin_client.get(f"/bins/{bin.id}/image")
        assert response.status_code == 200

    def test_get_bin_image_not_found(self, auth_admin_client, bin, bin_image_file_path):
        with open(bin_image_file_path, "rb") as image_file:
            auth_admin_client.post(f"/bins/{bin.id}/image", data={"image": image_file})
        response = auth_admin_client.get(f"/bins/{bin.id+1}/image")
        assert response.status_code == 404

    def test_update_bin(self, auth_admin_client, bin):
        update_bin_data = {"description": "New description"}
        response = auth_admin_client.patch(f"/bins/{bin.id}", json=update_bin_data)
        assert response.status_code == 200

    def test_delete_bin(self, auth_admin_client, bin):
        response = auth_admin_client.delete(f"/bins/{bin.id}")
        assert response.status_code == 200
