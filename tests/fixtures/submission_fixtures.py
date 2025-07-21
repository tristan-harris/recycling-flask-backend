import pytest

from app.models import Submission

@pytest.fixture()
def submission_post_data(recyclable, user, bin):
    return \
    {
        "recyclable_id": recyclable.id,
        "user_id": user.id,
        "bin_id": bin.id,
        "latitude": bin.latitude,
        "longitude": bin.longitude,
    }

@pytest.fixture()
def submission_data(recyclable, user, bin):
    return \
    {
        "recyclable_id": recyclable.id,
        "user_id": user.id,
        "bin_id": bin.id,
        "latitude": bin.latitude,
        "longitude": bin.longitude,
        "status": "not_confirmed"
    }

@pytest.fixture()
def submission(db, submission_data):
    submission = Submission(**submission_data)
    db.session.add(submission)
    db.session.commit()
    return submission
