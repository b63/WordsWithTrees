from wordstree.db import init_db, get_db
from werkzeug.security import check_password_hash


def signup_login(client):
    name = 'acbdefghijklmnopqrstuvwxyz'
    username = '||66||'
    password = 'qwertY123'

    rv = client.post('/signup', data={
        'name': name,
        'username': username,
        'password': password,
        'password-confirm': password
    }, follow_redirects=True)

    user_id = get_db().execute('SELECT id FROM users WHERE username=? AND name=?', [username, name]).fetchone()[0]
    return {
        'username': username,
        'name': name,
        'password': password,
        'id': user_id
    }


def testing_signup(client, app):
    """
    Adding new account to the database through a post request and checking if info was added in the database correctly
    """
    db = get_db()
    cur = db.cursor()
    user = signup_login(client)

    cur.execute('SELECT id, name, username, hash_password FROM users WHERE id=?', [user['id']])
    user_content = cur.fetchone()

    assert user_content['name'] == user['name']
    assert user_content['username'] == user['username']
    assert check_password_hash(user_content['hash_password'], user['password'])


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
