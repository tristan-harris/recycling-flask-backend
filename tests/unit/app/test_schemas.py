from app import schemas

def test_registration_schema(user_data):
    assert schemas.validate_data(user_data, schemas.RegistrationSchema).valid

def test_registration_schema_minimal(user_data_minimal):
    assert schemas.validate_data(user_data_minimal, schemas.RegistrationSchema).valid

def test_registration_schema_invalid_email(user_data):
    user_data["email"] = "myemail"
    assert not schemas.validate_data(user_data, schemas.RegistrationSchema).valid

def test_registration_schema_missing_field(user_data):
    del user_data["email"]
    assert not schemas.validate_data(user_data, schemas.RegistrationSchema).valid

def test_login_schema_with_username(user_data):
    assert schemas.validate_data(
        {"username": user_data["username"], "password": user_data["password"]},
        schemas.LoginSchema).valid

def test_login_schema_with_email(user_data):
    assert schemas.validate_data(
        {"email": user_data["email"], "password": user_data["password"]},
        schemas.LoginSchema).valid

# should not be able to send both
def test_login_schema_with_username_and_email(user_data):
    assert not schemas.validate_data(
        {"username": user_data["username"], "email": user_data["email"], "password": user_data["password"]},
        schemas.LoginSchema).valid

def test_login_schema_no_username_or_email(user_data):
    assert not schemas.validate_data( {"password": user_data["password"]}, schemas.LoginSchema).valid

def test_submission_creation_schema():
    data = {"recyclable_id": 1, "user_id": 1, "bin_id": 1, "latitude": 1, "longitude": 1}
    assert schemas.validate_data(data, schemas.SubmissionCreationSchema).valid

# marshmallow automatically converts strings into ints/floats
def test_submission_creation_schema_coordinate_strings():
    data = {"recyclable_id": 1, "user_id": 1, "bin_id": 1, "latitude": "1.000", "longitude": "1"}
    assert schemas.validate_data(data, schemas.SubmissionCreationSchema).valid

def test_submission_creation_schema_invalid_data():
    data = {"recyclable_id": 1, "user_id": 1, "bin_id": 1, "latitude": "abc", "longitude": 1}
    assert not schemas.validate_data(data, schemas.SubmissionCreationSchema).valid
