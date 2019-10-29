import os
import sys
import tempfile
import pytest

from wordstree import app
from wordstree.app import init_db, get_db


@pytest.fixture
def client():
    db, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db)
    os.unlink(app.config['DATABASE'])


def test_homepage(client):
    """Test request to root path returns something resembling what it should. """
    data = client.get('/').data
    import sys
    print(sys.path)

    assert b'canvas' in data
