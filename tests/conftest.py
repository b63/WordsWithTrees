import os
import tempfile
import pytest

from wordstree import create_app
from wordstree.db import init_db, get_db


@pytest.fixture
def app():
    db_file, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    with app.app_context():
        init_db()
    yield app

    os.close(db_file)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


