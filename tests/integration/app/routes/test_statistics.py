import pytest


@pytest.mark.usefixtures("isolated_transactions")
class TestStatistics:
    def test_get_total_submissions(self, unauth_client, submission):
        response = unauth_client.get("/statistics")
        assert response.status_code == 200

    def test_get_total_submissions_no_entries(self, unauth_client):
        response = unauth_client.get("/statistics")
        assert response.status_code == 200
