from wordstree.db import get_db
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session

from .services import render_service
from .home import _initial_render

bp = Blueprint('buy', __name__)


@bp.route('/buy', methods=['GET'])
def buy_branches_get():
    """get all the branches that belong to the given user"""
    _initial_render()

    if session.get('user_id') is None:
        return redirect(url_for('login.login_as_get'))

    db = get_db()
    user_id = session['user_id']

    # Filter view if category specified in query string
    if "filter" in request.args:
        if request.args["filter"] == "visibility":
            cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id'
                             '= b.id WHERE available_for_purchase=1 ORDER BY b.depth ASC')
            available_branches = cur.fetchall()
        if request.args["filter"] == "price-high":
            cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id'
                             '= b.id WHERE available_for_purchase=1 ORDER BY branches_ownership.price DESC')
            available_branches = cur.fetchall()
        if request.args["filter"] == "price-low":
            cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id'
                             '= b.id WHERE available_for_purchase=1 ORDER BY branches_ownership.price ASC')
            available_branches = cur.fetchall()

    else:
        cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id'
                         '= b.id WHERE available_for_purchase=1 ORDER BY b.id DESC')
        available_branches = cur.fetchall()

    # get user's name and token amount
    cur = db.execute('SELECT name, token FROM users WHERE id = ?', [user_id])
    user = cur.fetchone()

    # get notifications for the user
    cur = db.execute('SELECT notifications.id, message FROM notifications '
                     'JOIN notification_objects ON notifications.entity_id = notification_objects.id '
                     'WHERE receiver_id = ?', [user_id])
    notifications = cur.fetchall()

    return render_template('buy_branch.html', branches=available_branches, user=user, notifications=notifications)


@bp.route('/buy/search', methods=['GET'])
def buy_branches_search():
    """search for branches that have similar text elements"""
    if session.get('user_id') is None:
        return redirect(url_for('login.login_as_get'))

    db = get_db()
    user_id = session['user_id']

    query = request.args['search_field']
    cur = db.execute("SELECT * FROM branches_ownership INNER JOIN branches b on branches_ownership.branch_id"
                     "= b.id WHERE text LIKE (?) ", ('%'+query+'%',))
    filtered_branches = cur.fetchall()
    # get user's name and token amount
    cur = db.execute('SELECT name, token FROM users WHERE id = ?', [user_id])
    user = cur.fetchone()

    # get notifications for the user
    cur = db.execute('SELECT notifications.id, message FROM notifications '
                     'JOIN notification_objects ON notifications.entity_id = notification_objects.id '
                     'WHERE receiver_id=?', [user_id])
    notifications = cur.fetchall()

    return render_template('buy_branch.html', branches=filtered_branches, user=user, notifications=notifications)


@bp.route('/buy/branch', methods=['POST'])
def buy_branch():
    """purchase a branch and change the contents of a the branch"""
    db = get_db()
    buying_id = request.form["branch_id"]
    branch_price = request.form["branch_price"]
    branch_text = request.form['new-bt']
    user_id = session['user_id']

    cur = db.execute('SELECT token FROM users WHERE id = ?', [user_id])
    token = cur.fetchone()["token"]

    if token <= int(branch_price):
        # insert insufficient tokens notification
        db.execute("INSERT INTO notifications (receiver_id, entity_id) VALUES (?, ?)", [user_id, 6])
        db.commit()
        return redirect(url_for("buy.buy_branches_get"))
    else:
        cur = db.execute('SELECT owner_id FROM branches_ownership WHERE branch_id= ?', [buying_id])
        old_owner_id = cur.fetchone()["owner_id"]

        db.execute('UPDATE branches_ownership SET owner_id = ?, text = ?, available_for_purchase = 0 '
                   'WHERE branch_id=?', [user_id, branch_text, buying_id])
        db.execute('UPDATE users SET token = token - ? WHERE id = ?', [branch_price, user_id])
        db.execute('UPDATE users SET token = token + ? WHERE id = ?', [branch_price, old_owner_id])

        # insert sell branch successful notification for previous owner
        db.execute("INSERT INTO notifications (receiver_id, entity_id) VALUES (?, ?)", [old_owner_id, 5])
        db.commit()

        # insert buy branch successful notification
        db.execute("INSERT INTO notifications (receiver_id, entity_id) VALUES (?, ?)", [user_id, 3])
        db.commit()

        # re-render all tiles at all zoom levels in another thread
        render_service.render(zooms=None)

        return redirect(url_for("buy.buy_branches_get"))

