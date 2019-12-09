import os
import traceback
import json

from flask import Flask
from wordstree.db import get_db


def test_save_full_tree(app: Flask):
    """Test if svg of tree is saved after rendering tiles"""
    runner = app.test_cli_runner()

    result = runner.invoke(args=['render', '-z', '0-2', '-o', 'test_tree.json'])
    assert result.exception is None

    # check a new svg have been created
    with open(os.path.join(app.config['CACHE_DIR'], 'test_tree.json')) as f:
        tree = json.load(f)
        tree_name = tree['name']
    files = os.listdir(os.path.join(app.config['CACHE_DIR'], '{}/images/svg'.format(tree_name)))
    assert len(list(filter(lambda s: s.endswith('.svg'), files))) == 3


def test_add_to_db(app: Flask):
    """Test if branches are added to database"""
    runner = app.test_cli_runner()

    tree_id = 1
    result = runner.invoke(args=['render', '-d', '8', '-z', '0-1', '-o', 'db:{}'.format(tree_id)])
    assert result.exception is None

    with app.app_context():
        db = get_db()
        cur = db.cursor()

        # check entry to tree table was added
        cur.execute('SELECT * FROM tree WHERE tree_id=?', [tree_id])
        res = cur.fetchall()
        assert len(res) == 1

        # check correct number of branches added to branches table
        num_branches = res[0]['num_branches']
        cur.execute('SELECT * FROM branches WHERE tree_id=?', [tree_id])
        res2 = cur.fetchall()
        assert num_branches == len(res2)

        # check correct number of entries have been added to zoom_info
        cur.execute('SELECT zoom_id FROM zoom_info WHERE tree_id=?', [tree_id])
        res3 = cur.fetchall()
        assert res3 is not None and len(res3) == 2

        # check tiles information has been added to tiles table
        cur.execute('SELECT tile_id FROM tiles WHERE zoom_id IN (?, ?)', [res3[0]['zoom_id'], res3[1]['zoom_id']])
        res4 = cur.fetchall()
        assert res4 is not None and len(res4) > 0


def test_branch_grid_intersection(app: Flask):
    """Test if correct number of branches are recorded as being contained in a grid cell"""
    runner = app.test_cli_runner()

    tree_id = app.config['TEST_TREE_ID']
    result = runner.invoke(args=['render', '-z', '0', '--name=test_tree', '-f', 'db:{}'.format(tree_id)])
    assert result.exception is None

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT tree_name FROM tree WHERE tree_id=?', [tree_id])
        tree_name = cur.fetchone()['tree_name']

    test_cases = [
        # [(gridx, gridy), # of branches in the grid cell]
        [(2, 2), 9],
        [(1, 2), 9],
        [(2, 3), 1],
        [(3, 0), 0]
    ]
    success = 0
    total = len(test_cases)

    cache_dir = app.config['CACHE_DIR']
    dir = os.path.join(cache_dir, '{}/json/zoom_0'.format(tree_name))
    files = os.listdir(dir)

    for file in files:
        for case in test_cases:
            i, j = case[0]
            if file.endswith('{}_{}.json'.format(i, j)):
                # load json files and check for correct number of branches
                with open(os.path.join(dir, file), mode='r') as f:
                    assert len(json.load(f)) == case[1]
                success += 1

    assert success == total


def test_add_layer(app: Flask):
    """
    Tests `add-layer` cli command.
    """
    runner = app.test_cli_runner()

    # dummy tree should have no branches
    tree_id = app.config['DUMMY_TEST_TREE_ID']

    result = runner.invoke(args=['add-layer', '-f', 'db:{}'.format(tree_id), '-n', '1'])
    assert result.exception is None

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM branches  WHERE tree_id=?', [tree_id])
        res = cur.fetchall()

        # there should only be the root branch
        assert len(res) == 1
        row = res[0]
        assert row['depth'] == 0

    # test if entries are added to branches_ownership
    dummy_id = app.config['DUMMY_USER_ID']
    result = runner.invoke(args=['add-layer', '-f', 'db:{}'.format(tree_id), '-n', 2, '--owner-id', dummy_id])
    assert result.exception is None

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT DISTINCT depth, tree_id FROM branches  WHERE tree_id=?', [tree_id])
        res = cur.fetchall()

        # there should be 3 layers now
        assert len(res) == 3

        # number of new branches added
        cur.execute('SELECT * FROM branches WHERE tree_id=? AND depth > 0', [tree_id])
        num_branches = len(cur.fetchall())

        # all of them should have corresponding entries in branches_ownership with owner_id of dummy_id
        cur.execute('SELECT * FROM branches INNER JOIN branches_ownership bo on branches.id = bo.branch_id '
                    'WHERE bo.owner_id=?', [dummy_id])
        assert num_branches == len(cur.fetchall())
