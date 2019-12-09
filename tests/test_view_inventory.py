from wordstree.db import init_db, get_db


def signup_login(client):
    client.post('/signup', data={
        'name': 'Person',
        'username': 'nick',
        'password': 'qwertY123',
        'password-confirm': 'qwertY123'}, follow_redirects=True)
    return get_db().execute('SELECT id FROM users WHERE username=?', ['nick']).fetchone()[0]


def insert_branch(app, text, depth, ind, owner_id, sell):
    # dummy tree has no branches
    test_tree_id = app.config['DUMMY_TEST_TREE_ID']
    db = get_db()
    cur = db.cursor()
    db.execute(
        'INSERT INTO branches (ind, depth, length, width, angle, pos_x, pos_y, tree_id) VALUES'
        '(?, ?, ?, ?, ?, ?, ?, ?)',
        [ind, depth, 10, 10, 0.1, 0, 0, test_tree_id]
    )
    branch_id = cur.execute('select last_insert_rowid()').fetchone()[0]
    db.execute(
        'INSERT INTO branches_ownership (branch_id, owner_id, text, available_for_purchase) VALUES'
        '(?, ?, ?, ?)',
        [branch_id, owner_id, text, sell]
    )
    db.commit()

    return branch_id


def test_view_inventory(client, app):
    with app.app_context():
        user_id = signup_login(client)
        insert_branch(app, text="Branch 1", depth=1, ind=1, owner_id=user_id, sell=0)
        insert_branch(app, text="Branch 2", depth=1, ind=2, owner_id=user_id, sell=0)
        rv = client.get('/inventory', follow_redirects=True)
        assert b'Branch 1' in rv.data
        assert b'Branch 2' in rv.data


def test_sell_branch(client, app):
    with app.app_context():
        user_id = signup_login(client)
        insert_branch(app, text="Branch 1", depth=1, ind=1, owner_id=user_id, sell=0)
        rv = client.post('sell', data=dict(
            selling_price=20,
            branch_id=1), follow_redirects=True)
        assert b'Branch 1' not in rv.data
