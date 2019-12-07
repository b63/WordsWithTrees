from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import generate_password_hash

bp = Blueprint('buy', __name__)


def insert_branch(text, depth, ind, owner_id, sell, db):
    cur = db.cursor()
    db.execute(
        'INSERT INTO branches (ind, depth, length, width, angle, pos_x, pos_y, tree_id) VALUES'
        '(?, ?, ?, ?, ?, ?, ?, 1)',
        [ind, depth, 1, 10, 0.1, 0, 0]
    )
    branch_id = cur.execute('select last_insert_rowid()').fetchone()[0]
    db.execute(
        'INSERT INTO branches_ownership (branch_id, owner_id, text, available_for_purchase) VALUES'
        '(?, ?, ?, ?)',
        [branch_id, owner_id, text, sell]
    )
    db.commit()


@bp.route('/buy', methods=['GET'])
def buy_branches_get():
    """get all the branches that belong to the given user"""
    db = get_db()

    # Filter view if category specified in query string
    if "filter" in request.args:
        if request.args["filter"] == "visibility":
            cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id'
                             '= b.id WHERE available_for_purchase=1 ORDER BY b.depth DESC')
            available_branches = cur.fetchall()
        if request.args["filter"] == "price":
            cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id'
                             '= b.id WHERE available_for_purchase=1 ORDER BY branches_ownership.price DESC')
            available_branches = cur.fetchall()
    else:
        cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id'
                         '= b.id WHERE available_for_purchase=1 ORDER BY b.id DESC')
        available_branches = cur.fetchall()

    return render_template('buy_branch.html', branches=available_branches)


@bp.route('/buy/search', methods=['GET'])
def buy_branches_search():
    """search for branches that have similar text elements"""
    db = get_db()
    query = request.args['search_field']
    cur = db.execute("SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id"
                     "= b.id WHERE text LIKE (?) ",('%'+query+'%',))
    filtered_branches = cur.fetchall()
    return render_template('buy_branch.html', branches=filtered_branches)


@bp.route('/buy/branch', methods=['POST'])
def buy_branch():
    """purchase a branch and change the contents of a the branch"""
    db = get_db()
    buying_id = request.form["branch_id"]
    user_id = session['user_id']
    print(buying_id)
    db.execute('UPDATE branches_ownership SET owner_id=? WHERE id=?', [user_id,buying_id])
    db.execute('UPDATE branches_ownership SET text=? WHERE id=?', [request.form['new-bt'],buying_id])
    db.execute('UPDATE branches_ownership SET available_for_purchase=0 WHERE id=?', [buying_id])
    db.commit()
    return redirect(url_for("buy.buy_branches_get"))

