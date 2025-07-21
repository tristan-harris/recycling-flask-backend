import pytest

from app.models import Purchase

@pytest.fixture()
def purchase_data(user, reward):
    return \
    {
        "user_id": user.id,
        "reward_id": reward.id,
        "quantity": 1
    }

@pytest.fixture()
def purchase(db, purchase_data):
    purchase = Purchase(**purchase_data)
    db.session.add(purchase)
    db.session.commit()
    return purchase
