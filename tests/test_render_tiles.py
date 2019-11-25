from flask import Flask
import os


def test_render_zoom(app: Flask):
    """Test if branches are written to JSON file."""
    runner = app.test_cli_runner()

    result = runner.invoke(args=['render-tiles', '-z', '0-2', '-o', 'test_tree.json'])
    # check if branches were written to file
    assert os.path.exists(os.path.join(app.config['CACHE_DIR'], 'test_tree.json'))



