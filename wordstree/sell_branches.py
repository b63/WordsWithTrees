from wordstree.db import get_db
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
import sys

bp = Blueprint('sell', __name__)


@bp.route('/sell', methods=['POST'])
def sell_branches_post():
    """ Convert branch to available for purchase as requested by user. """
    # TODO: check if the current user in session has required permission to modify the branch
    db = get_db()
    db.execute('UPDATE branches_ownership SET price=?, available_for_purchase=1 WHERE branch_id=?',
               [request.form["selling_price"], request.form["branch_id"]])
    db.commit()

    return redirect(url_for("view_inventory.view_inventory"))
