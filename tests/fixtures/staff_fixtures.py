import pytest

from app.models import Staff

@pytest.fixture()
def staff_data(user):
    return \
    {
        "user_id": user.id,
        "role": "admin",
    }

@pytest.fixture()
def staff(db, staff_data):
    staff = Staff(**staff_data)
    db.session.add(staff)
    db.session.commit()
    return staff
