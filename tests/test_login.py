import os
import sys
import tempfile
import pytest
from flask import current_app, session
from wordstree.db import init_db, get_db
from werkzeug.security import check_password_hash, generate_password_hash

def register_user(name, username, password):
    db = get_db()
    password = password
    hash_password = generate_password_hash(password)
    db.execute("INSERT INTO users (name, username, hash_password) VALUES (?, ?, ?)",
                [name, username, hash_password])
    cur = db.execute('SELECT name, username, hash_password FROM users')
    user_content = cur.fetchone()
    assert user_content['name'] == name
    assert user_content['username'] == username
    assert check_password_hash(user_content['hash_password'], password)


'''testing logging in with predetermined credentials'''
def test_login(client, app):
    with app.app_context():
        # testing if we are correctly getting the login page
        assert client.get('/login').status_code == 200
        # registering a user and checking if their session is active
        name, username, password = 'test', 'testy', 'qwertY123'
        register_user(name, username, password)
        rv = client.post('/login', data={
            'username': username,
            'password': password}, follow_redirects=True)
        with client:
            client.get('/')
            assert session['user_id'] == 1





