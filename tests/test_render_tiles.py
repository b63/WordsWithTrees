import os
import json


from flask import Flask
from wordstree.db import get_db


def test_save_full_tree(app: Flask):
    """Test if svg of tree is saved after rendering tiles"""
    runner = app.test_cli_runner()

    result = runner.invoke(args=['render-tiles', '-z', '0-2', '-o', 'test_tree.json'])
    assert result.exception is None

    # check a new svg have been created
    files = os.listdir(os.path.join(app.config['IMAGE_DIR'], 'svg'))
    assert len(list(filter(lambda s: s.endswith('.svg'), files))) == 3


def test_add_to_db(app: Flask):
    """Test if branches are added to database"""
    runner = app.test_cli_runner()

    tree_id = 1
    result = runner.invoke(args=['render-tiles', '-d', '8', '-z', '0', '-o', 'db:{}'.format(tree_id)])
    assert result.exception is None

    with app.app_context():
        db = get_db()
        cur = db.cursor()

        cur.execute('SELECT * FROM tree WHERE tree_id=?', [tree_id])

        # check entry to tree table was added
        res = cur.fetchall()
        assert len(res) == 1

        # check correct number of branches added to branches table
        num_branches = res[0]['num_branches']
        cur.execute('SELECT * FROM branches WHERE tree_id=?', [tree_id])
        res2 = cur.fetchall()

        assert num_branches == len(res2)


def test_branch_grid_intersection(app: Flask):
    """Test if correct number of branches are recorded as being contained in a grid cell"""
    runner = app.test_cli_runner()

    tree_id = app.config['TEST_TREE_ID']
    result = runner.invoke(args=['render-tiles', '-z', '0', '-f', 'db:{}'.format(tree_id)])
    assert result.exception is None

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
    dir = os.path.join(cache_dir, 'json/zoom_0')
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
