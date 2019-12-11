from wordstree.db import get_db
import flask
from flask import current_app

from .test_login import register_user
from .test_signup import signup_login


# hashmap to store indices of branch entries already added to database
__cache = set()


def insert_branch(depth=0, ind=None, owner_id=None, text='', sell=False):
    """
    Insert branch into `branches` table and an entry to `branches_ownership` table with the given owner-id, text, and
    availability of purchase.
    Note: requires application context

    :param ind: index of branch
    :param depth: depth of branch
    :param owner_id: id of entry in `users` table
    :param text: value of `text` column for entry in `branches_ownership` table
    :param sell: whether the branch is available for purchase
    :return: the id of the newly inserted entry in the `branches` table
    """
    if not flask.has_app_context():
        raise Exception('app_context not pushed to application context stack')

    app = current_app
    # dummy tree has no branches
    test_tree_id = app.config['DUMMY_TEST_TREE_ID']

    db = get_db()
    cur = db.cursor()

    if ind is None:
        # find index that's not already used
        ind = 0
        while (test_tree_id, ind) in __cache:
            ind += 1

    cur.execute(
        'INSERT INTO branches (ind, depth, length, width, angle, pos_x, pos_y, tree_id) VALUES'
        '(?, ?, ?, ?, ?, ?, ?, ?)',
        [ind, depth, 10, 10, 0, 0, 0, test_tree_id]
    )
    branch_id = cur.execute('select last_insert_rowid()').fetchone()[0]
    __cache.add((test_tree_id, ind))

    if owner_id:
        sell = 1 if sell else 0
        cur.execute(
            'INSERT INTO branches_ownership (branch_id, owner_id, text, available_for_purchase) VALUES'
            '(?, ?, ?, ?)',
            [branch_id, owner_id, text, sell]
        )

    return branch_id


def test_buy_branches(client, app):
    """
    Test if post request to /buy/branch for change of ownership of a branch is reflected in the `branches_ownership`
    table.
    """
    db = get_db()
    cur = db.cursor()

    # sign up user 1
    user1_id = register_user('ted', 'ted', 'qwertyY123')

    branch_id = insert_branch(owner_id=user1_id, text='Branch 1', sell=True)
    branch_id2 = insert_branch(owner_id=user1_id, text='Branch 2', sell=True)

    # sign up and login user 2
    user = signup_login(client)

    # buy branch
    client.post('/buy/branch', data={
        'new-bt': 'new Branch',
        'branch_id': branch_id,
        'branch_price': 10
    }, follow_redirects=True)

    cur.execute('SELECT text, users.id, users.token FROM branches_ownership INNER JOIN users ON '
                'branches_ownership.owner_id = users.id WHERE owner_id=?;', [user['id']])
    row = cur.fetchone()

    assert row["text"] == "new Branch"
    assert row["token"] == 90

