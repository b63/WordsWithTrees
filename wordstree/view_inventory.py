from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session

bp = Blueprint('view_inventory', __name__)


@bp.route('/inventory')
def view_inventory():
    """ Display user's inventory. """
    db = get_db()

    cur = db.execute('SELECT * FROM branches')
    branches = cur.fetchall()

    return render_template("view_inventory.html", branches=branches)


