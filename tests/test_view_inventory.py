from .test_buy_branch import insert_branch
from .test_signup import signup_login


def test_view_inventory(client, app):
    user = signup_login(client)
    insert_branch(text="Branch 1", owner_id=user['id'])
    insert_branch(text="Branch 2", owner_id=user['id'])
    rv = client.get('/inventory', follow_redirects=True)
    assert b'Branch 1' in rv.data
    assert b'Branch 2' in rv.data


def test_sell_branch(client, app):
    user = signup_login(client)
    branch_id = insert_branch(owner_id=user['id'], text="Branch 1", sell=False)
    rv = client.post('/sell', data=dict(selling_price=20, branch_id=branch_id), follow_redirects=True)
    assert b'Branch 1' not in rv.data
