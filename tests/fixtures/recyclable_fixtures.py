import pytest

from app.models import Recyclable

@pytest.fixture()
def recyclable_data():
    return \
    {
        "type": "cardboard",
        "points_value": 10_000,
        "description": "Cardboard Box",
        "weight": 10
    }

@pytest.fixture()
def recyclable(db, recyclable_data):
    recyclable = Recyclable(**recyclable_data)
    db.session.add(recyclable)
    db.session.commit()
    return recyclable
