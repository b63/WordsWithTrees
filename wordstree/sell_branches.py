from wordstree.db import get_db
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
import sys

bp = Blueprint('sell', __name__)


@bp.route('/sell', methods=['POST'])
def sell_branches_post():
    """ Convert branch to available for purchase as requested by user. """
    if session.get('user_id') is None:
        return redirect(url_for('login.login_as_get'))

    user_id = session['user_id']

    db = get_db()
    db.execute('UPDATE branches_ownership SET price=?, available_for_purchase=1 WHERE branch_id=?',
               [request.form["selling_price"], request.form["branch_id"]])
    db.commit()

    # insert sell branch waiting for buyer notification
    db.execute("INSERT INTO notifications (receiver_id, entity_id) VALUES (?, ?)", [user_id, 4])
    db.commit()

    return redirect(url_for("view_inventory.view_inventory"))
