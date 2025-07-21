import pytest

from app.models import Motivation

@pytest.fixture()
def motivation_data(user):
    return {"user_id": user.id, "motivation": "Motivation text"}

@pytest.fixture()
def motivation(db, motivation_data):
    motivation = Motivation(**motivation_data)
    db.session.add(motivation)
    db.session.commit()
    return motivation
