from wordstree.db import init_db, get_db
from werkzeug.security import check_password_hash, generate_password_hash

def signup_login(client):
    return client.post('/signup', data={
        'name': 'Person',
        'username': 'nick',
        'password': 'qwertY123',
        'password-confirm': 'qwertY123'}, follow_redirects=True)


def insert_branch(app, text, depth, ind, owner_id, sell):
    # dummy tree has no branches
    test_tree_id = app.config['DUMMY_TEST_TREE_ID']
    with app.app_context():
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


def test_buy_branches(client, app):
    with app.app_context():
        db = get_db()
        signup_login(client)
        password = 'qwertY123'
        hash_password = generate_password_hash(password)
        db.execute("INSERT INTO users (name, username, hash_password) VALUES (?, ?, ?)",
                   ['ted','ted', hash_password])
        db.commit()
        insert_branch(app, "Branch 1", 1, 1, 2, 1)
        insert_branch(app, "Branch 2", 1, 2, 2, 1)
        cur = db.execute('SELECT branch_id FROM branches_ownership WHERE text="Branch 1"')
        branch_id = cur.fetchone()
        print(type(branch_id["branch_id"]))
        rv = client.post('/buy/branch', data={
            'new-bt': 'new Branch',
            'branch_id': branch_id["branch_id"]
        }, follow_redirects=True)

        rv.data

        cur = db.execute('SELECT text FROM branches_ownership WHERE owner_id=1')
        branch = cur.fetchone()

        assert branch["text"] == "new Branch"
