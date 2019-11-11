from wordstree.db import init_db, get_db


def signup_login(client):
    return client.post('/register', data={
        'name': 'Person',
        'username': 'nick',
        'password': 'qwertY123',
        'password-confirm': 'qwertY123'}, follow_redirects=True)


def test_view_inventory(client, app):
    signup_login(client)
    rv = client.get('/view?id=1', follow_redirects=True)
    with app.app_context():
        db = get_db()
        cur = db.execute('INSERT INTO branches VALUES ')
        db.commit()
    #rv.data
