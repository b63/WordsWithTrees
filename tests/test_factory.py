from wordstree import create_app


def test_factory_config():
    """Test `test_config` argument passed to application factory"""
    assert not create_app(test_config=None).config['TESTING']
    assert create_app(test_config={'TESTING': True}).config['TESTING']


def test_homepage(client):
    """Test request to root path returns something resembling what it should. """
    data = client.get('/').data

    assert b'canvas' in data
