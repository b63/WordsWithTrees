import flask
from wordstree.db import init_db, get_db
from werkzeug.security import check_password_hash, generate_password_hash


def insert_branch(app, text, depth, ind, owner_id, sell):
    # dummy tree has no branches
    test_tree_id = app.config['DUMMY_TEST_TREE_ID']

    db = get_db()
    cur = db.cursor()
    cur.execute(
        'INSERT INTO branches (ind, depth, length, width, angle, pos_x, pos_y, tree_id) VALUES'
        '(?, ?, ?, ?, ?, ?, ?, ?)',
        [ind, depth, 10, 10, 0.1, 0, 0, test_tree_id]
    )
    branch_id = cur.execute('select last_insert_rowid()').fetchone()[0]
    cur.execute(
        'INSERT INTO branches_ownership (branch_id, owner_id, text, available_for_purchase) VALUES'
        '(?, ?, ?, ?)',
        [branch_id, owner_id, text, sell]
    )


def test_buy_branches(client, app):
    with app.app_context():
        db = get_db()
        cur = db.cursor()

        # sign up user 2
        cur.execute('INSERT INTO users (name, username, hash_password) VALUES (?, ?, ?);',
                    ['ted', 'ted', generate_password_hash('qwertY123')])
        user2_id = cur.execute('select last_insert_rowid()').fetchone()[0]

        insert_branch(app, text='Branch 1', depth=1, ind=1, owner_id=user2_id, sell=1)

        cur.execute('SELECT branch_id FROM branches_ownership WHERE text=\'Branch 1\';')
        row = cur.fetchone()
        branch_id = row[0]

        # sign up and login user1
        client.post('/signup', data={
            'name': 'Person',
            'username': 'nick',
            'password': 'qwertY123',
            'password-confirm': 'qwertY123'
        }, follow_redirects=True)
        # get user_id
        cur.execute('SELECT id FROM users WHERE username=?', ['nick'])
        user1_id = cur.fetchone()[0]

        # buy branch
        client.post('/buy/branch', data={
            'new-bt': 'new Branch',
            'branch_id': branch_id
        }, follow_redirects=True)

        cur.execute('SELECT text FROM branches_ownership WHERE owner_id=?;', [user1_id])
        row = cur.fetchone()

        assert row[0] == 'new Branch'
