from wordstree.db import init_db, get_db

def signup_login(client):
    return client.post('/signup', data={
        'name': 'Person',
        'username': 'nick',
        'password': 'qwertY123',
        'password-confirm': 'qwertY123'}, follow_redirects=True)

def insert_branch(app, text, depth, ind, owner_id, sell):
    with app.app_context():
        db = get_db()
        cur = db.cursor()

        db.execute(
            'INSERT INTO branches (ind, depth, length, width, angle, pos_x, pos_y, tree_id) VALUES'
            '(?, ?, ?, ?, ?, ?, ?, 1)',
            [ind, depth, 10, 10, 0.1, 0, 0]
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
        print("jg")
        signup_login(client)
        insert_branch(app, "Branch 1", 1, 1, 1, 0)
        insert_branch(app, "Branch 2", 1, 2, 1, 1)
        rv = client.post('/buy ', data={
            'new-db': 'new Branch',
            'branch_id': 2
        }, follow_redirects=True)
        db = get_db()
        # print("hello there")
        # cur = db.execute('SELECT text FROM branches_ownership WHERE id=1')
