from pathlib import Path

import pytest

from app.models import Reward

@pytest.fixture()
def reward_data():
    return \
    {
        "title": "Reward title",
        "description": "Reward description",
        "price": 100
    }

@pytest.fixture()
def reward(db, reward_data):
    reward = Reward(**reward_data)
    db.session.add(reward)
    db.session.commit()
    return reward

@pytest.fixture()
def reward_image_file_path():
    return Path("tests/resources/images/rewards/reward.jpg")
