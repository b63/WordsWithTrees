from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import generate_password_hash

bp = Blueprint('buy', __name__)


@bp.route('/buy', methods=['GET'])
def buy_branches_get():
    """get all the branches that belong to the given user"""
    db = get_db()

    user_id = session['user_id']

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

    cur = db.execute('SELECT name, token FROM users WHERE id = ?', str(user_id))
    user = cur.fetchone()

    return render_template('buy_branch.html', branches=available_branches, user=user)

#
# @bp.route('/buy', methods =['POST'])
# def buy_branches():
#     """ in progress... """
#     """buy branches that are selected by the user"""
#     # we want to include a modal
#     return
