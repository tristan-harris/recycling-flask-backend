from pathlib import Path

import pytest

from app.models import AllowedRecyclable, Bin

@pytest.fixture()
def bin_data():
    return \
    {
        "latitude": 1.0,
        "longitude": 1.0,
        "name": "Test Bin",
        "description": "Description of Test Bin",
    }

@pytest.fixture()
def bin(db, bin_data):
    bin = Bin(**bin_data)
    db.session.add(bin)
    db.session.commit()
    return bin

@pytest.fixture()
def bin_with_whitelist(db, recyclable, bin_data):
    bin_whitelist_data = bin_data
    bin_whitelist_data["whitelist"] = True
    bin = Bin(**bin_whitelist_data)
    db.session.add(bin)
    db.session.commit()

    allowed_recyclable = AllowedRecyclable(**{"bin_id": bin.id, "recyclable_id": recyclable.id})
    db.session.add(allowed_recyclable)
    db.session.commit()

    return bin

@pytest.fixture()
def bin_image_file_path():
    return Path("tests/resources/images/recycling-bins/recycling-bins.jpg")
