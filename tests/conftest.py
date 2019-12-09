import os
import shutil
import tempfile
import pytest

from wordstree import create_app
from wordstree.db import init_db, get_db


@pytest.fixture
def app():
    db_file, db_path = tempfile.mkstemp()
    cache_path = tempfile.mkdtemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'CACHE_DIR': cache_path,
        'IMAGE_DIR': os.path.join(cache_path, 'images'),
        'TEST_TREE_ID': 1938,  # tree has of branches
        'DUMMY_TEST_TREE_ID': 1945,  # tree has no branches
        'DUMMY_USER_ID': 2099  # tree has no branches
    })

    with app.app_context():
        init_db(exclude=['70-dummy.sql'])
    yield app

    os.close(db_file)
    os.unlink(db_path)
    shutil.rmtree(cache_path)


@pytest.fixture
def client(app):
    return app.test_client()
