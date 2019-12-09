import os
import sys
import tempfile
import pytest
from flask import current_app
from wordstree.db import init_db, get_db
from werkzeug.security import check_password_hash


def testing_signup(client, app):
    """
    Adding new account to the database through a post request and checking if info was added in the database correctly
    """
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        rv = client.post('/signup', data={
            'name': 'Person',
            'username': 'nick',
            'password': 'qwertY123',
            'password-confirm': 'qwertY123'}, follow_redirects=True)

        cur.execute('SELECT id FROM users WHERE username=?', ['nick'])
        user_id = cur.fetchone()[0]

        cur = db.execute('SELECT id, name, username, hash_password FROM users WHERE id=?', [user_id])
        user_content = cur.fetchone()

        assert user_content['name'] == 'Person'
        assert user_content['username'] == 'nick'
        assert check_password_hash(user_content['hash_password'], 'qwertY123')


def test_flash_messages(client):
    # testing name
    rv = client.post('/signup', data={
        'username': 'nick',
        'password': 'qwertY123',
        'password-confirm': 'qwertY123'}, follow_redirects=True)
    cur = rv.data
    assert b'You must provide a name' in cur

    # testing flash for username
    rv = client.post('/signup', data={
        'name': 'Person',
        'password': 'qwertY123',
        'password-confirm': 'qwertY123'}, follow_redirects=True)
    cur = rv.data
    assert b'You must provide a username' in cur

    # testing flash for username
    rv = client.post('/signup', data={
        'name': 'Person',
        'username': 'nick',
        'password-confirm': 'qwertY123'}, follow_redirects=True)
    cur = rv.data
    assert b'You must provide a password' in cur

    # testing flash for username
    rv = client.post('/signup', data={
        'name': 'Person',
        'username': 'nick',
        'password': 'qwertY123'}, follow_redirects=True)
    cur = rv.data
    assert b'You must provide a password confirmation' in cur

    # testing flash for username
    rv = client.post('/signup', data={
        'name': 'Person',
        'username': 'nick',
        'password': 'qwertY123',
        'password-confirm': 'qwertY124'}, follow_redirects=True)
    cur = rv.data
    assert b'Your passwords must match' in cur


'''testing deletion of a post with a given id and checking for the right change in the 
    database and in the site data'''
# def test_delete_database(client):
#
#     client.post('/add', data = {
#         'title':'before title',
#         'category': 'before category',
#         'text':'before text'})
#     db = get_db()
#     cur = db.execute('SELECT title, category, text FROM entries WHERE id=1')
#     post_content = cur.fetchone()
#     assert post_content['title'] == 'before title'
#     assert post_content['category'] == 'before category'
#     assert post_content['text'] == 'before text'
#     client.post('/delete', data={'id': 1})
#     db = get_db()
#     cur = db.execute('SELECT title, category, text FROM entries WHERE id=1')
#     del_content = cur.fetchone()
#     assert del_content == None
#     # testing for the deletion of contents in the database
#     site = client.get('/')
#     assert b'before title' not in site.data
#     assert b'before category' not in site.data
#     assert b'before text' not in site.data
