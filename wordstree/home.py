from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import generate_password_hash

bp = Blueprint('root', __name__)


def _initial_branches(num_layers):
    tree_id = current_app.config['TREE_ID']
    try:
        current_app.cli.get_command(current_app, 'add-layer').main(args=[
            '-f', 'db:{}'.format(tree_id), '-n', num_layers, '--owner-id=666', '--bid=True', '--text=HOUSE'
        ])
    except SystemExit:
        pass


def _initial_render():
    tree_id = current_app.config['TREE_ID']

    db = get_db()
    res = db.execute('SELECT * FROM zoom_info WHERE tree_id=?', [tree_id]).fetchall()

    if (res is None or len(res) == 0) and not current_app.config['TESTING']:
        # if not testing, render all branches once
        _initial_branches(1)
        from .services import render_service
        render_service.render(zooms=None)


@bp.route('/')
def home():
    """ Handles requests to the root page """
    _initial_render()

    user_id = session['user_id']

    db = get_db()
    row = db.execute('SELECT id FROM users WHERE id=?', [user_id]).fetchone()

    if row is not None:
        return redirect(url_for("view_inventory.view_inventory"))
    else:
        return render_template('index.html')


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


