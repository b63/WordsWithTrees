from flask import current_app, session
from wordstree.db import init_db, get_db
from werkzeug.security import check_password_hash, generate_password_hash


def register_user(name, username, password):
    db = get_db()
    cur = db.cursor()

    hash_password = generate_password_hash(password)
    cur.execute("INSERT INTO users (name, username, hash_password) VALUES (?, ?, ?)",
               [name, username, hash_password])
    cur.execute('SELECT last_insert_rowid();')
    user_id = cur.fetchone()[0]

    cur.execute('SELECT id, name, username, hash_password FROM users WHERE id=?', [user_id])
    row = cur.fetchone()
    assert row['name'] == name
    assert row['username'] == username
    assert check_password_hash(row['hash_password'], password)

    return user_id


def test_login(client, app):
    """testing logging in with predetermined credentials"""
    with app.app_context():
        # testing if we are correctly getting the login page
        assert client.get('/login').status_code == 200
        # registering a user and checking if their session is active
        name, username, password = 'test', 'testy', 'qwertY123'
        user_id = register_user(name, username, password)
        rv = client.post('/login', data={
            'username': username,
            'password': password}, follow_redirects=True)
        with client:
            client.get('/')
            assert session['user_id'] == user_id
