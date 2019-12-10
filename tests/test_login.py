from flask import current_app, session
from wordstree.db import init_db, get_db
from werkzeug.security import generate_password_hash


def register_user(name, username, password):
    """
    Add an entry to `users` table with the given credentials.
    :param name: name
    :param username: username
    :param password: password
    :return: the `id` of the entry in `users` table
    """
    db = get_db()
    cur = db.cursor()

    hash_password = generate_password_hash(password)
    cur.execute("INSERT INTO users (name, username, hash_password) VALUES (?, ?, ?)",
                [name, username, hash_password])
    cur.execute('SELECT last_insert_rowid();')
    user_id = cur.fetchone()[0]

    return user_id


def test_login(client, app):
    """Testing logging in with predetermined credentials."""
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
