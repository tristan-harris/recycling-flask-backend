import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from app import create_app, db as _db

from tests.fixtures.bin_fixtures import *
from tests.fixtures.motivation_fixtures import *
from tests.fixtures.purchase_fixtures import *
from tests.fixtures.recyclable_fixtures import *
from tests.fixtures.reward_fixtures import *
from tests.fixtures.staff_fixtures import *
from tests.fixtures.submission_fixtures import *
from tests.fixtures.user_fixtures import *

@pytest.fixture(scope="session")
def test_config(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("uploads")

    return \
    {
        "TESTING": True,
        "DATABASE_NAME": "recycling_project_TEST",
        "UPLOADS_DIRECTORY": str(tmp_path),
    }

@pytest.fixture(scope="session")
def app(test_config):
    test_app = create_app(test_config)
    with test_app.app_context():
        _db.create_all()
    yield test_app
    with test_app.app_context():
        _db.drop_all()

@pytest.fixture(scope="session")
def db():
    return _db

# ensures that each database transaction is rolled back at the end of a test
@pytest.fixture()
def isolated_transactions(app, db):
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        # override global session for test
        db.session = scoped_session(
            session_factory=sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
        )

        yield

        db.session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture()
def client(app):
    test_client = app.test_client()
    return test_client
