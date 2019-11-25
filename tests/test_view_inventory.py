from wordstree.db import init_db, get_db


def signup_login(client):
    return client.post('/signup', data={
        'name': 'Person',
        'username': 'nick',
        'password': 'qwertY123',
        'password-confirm': 'qwertY123'}, follow_redirects=True)
def insert_branch(app,text, depth, ind, owner_id, price, color, sell):
    with app.app_context():
        db = get_db()
        cur = db.execute('INSERT INTO branches(text, depth, ind, owner_id, price, color, sell) VALUES(?,?,?,?,?,?,?)',
        [text, depth, ind, owner_id, price, color, sell])
        db.commit()

def test_view_inventory(client, app):
    signup_login(client)
    insert_branch(app, "Branch 1", 1, 1, 1, 100, 'blue', 0)
    insert_branch(app, "Branch 2", 1, 2, 2, 100, 'blue', 0)
    rv = client.get('/inventory', follow_redirects=True)
    point = rv.data
    assert b'Branch 1' in point
    assert b'Branch 2' not in point

