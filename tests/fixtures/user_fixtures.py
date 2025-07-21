from flask_jwt_extended import create_access_token
import pytest
from werkzeug.security import generate_password_hash

from app.models import User, Staff

_password = "password"

@pytest.fixture()
def password():
    return _password

@pytest.fixture()
def user_data():
    return \
    {
        "username": "TheUser",
        "password": generate_password_hash(_password),
        "email": "user@user.com",
        "phone_number": "111",
        "first_name": "User",
        "last_name": "User",
        # "date_of_birth": "1990-01-01",
        "age": 100,
    }

@pytest.fixture()
def user_data_minimal():
    return \
    {
        "username": "TheUser",
        "password": generate_password_hash(_password),
        "email": "user@user.com",
        # "date_of_birth": "1990-01-01",
        "age": 100,
    }

@pytest.fixture()
def moderator_data():
    return \
    {
        "username": "TheModerator",
        "password": generate_password_hash(_password),
        "email": "moderator@moderator.com",
        "phone_number": "222",
        "first_name": "Moderator",
        "last_name": "Moderator",
        # "date_of_birth": "1990-01-01",
        "age": 100,
    }

@pytest.fixture()
def admin_data():
    return \
    {
        "username": "TheAdmin",
        "password": generate_password_hash(_password),
        "email": "admin@admin.com",
        "phone_number": "333",
        "first_name": "Admin",
        "last_name": "Admin",
        # "date_of_birth": "1990-01-01",
        "organisation": "University",
        "age": 100,
    }

@pytest.fixture()
def user(db, user_data):
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture()
def moderator(db, moderator_data):
    moderator = User(**moderator_data)
    db.session.add(moderator)
    db.session.commit()

    moderator_staff_entry = Staff(**{"user_id": moderator.id, "role": "moderator"})
    db.session.add(moderator_staff_entry)
    db.session.commit()

    return moderator

@pytest.fixture()
def admin(db, admin_data):
    admin = User(**admin_data)
    db.session.add(admin)
    db.session.commit()

    admin_staff_entry = Staff(**{"user_id": admin.id, "role": "admin"})
    db.session.add(admin_staff_entry)
    db.session.commit()

    return admin

@pytest.fixture()
def unauth_client(client):
    return client

@pytest.fixture()
def auth_user_client(client, user):
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {create_access_token(identity=user)}"
    return client

@pytest.fixture()
def auth_mod_client(client, moderator):
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {create_access_token(identity=moderator)}"
    return client

@pytest.fixture()
def auth_admin_client(client, admin):
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {create_access_token(identity=admin)}"
    return client
