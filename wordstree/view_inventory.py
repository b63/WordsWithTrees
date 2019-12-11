from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session

bp = Blueprint('view_inventory', __name__)


@bp.route('/inventory')
def view_inventory():
    """ Display user's inventory. """

    db = get_db()
    user_id = session['user_id']

    cur = db.execute('SELECT * FROM branches_ownership INNER JOIN branches b ON branches_ownership.branch_id = b.id'
                     ' WHERE owner_id = ? AND available_for_purchase = 0', [user_id])
    branches = cur.fetchall()

    cur = db.execute('SELECT name FROM users WHERE id = ?', [user_id])
    user = cur.fetchone()

    cur = db.execute('SELECT notifications.id, message FROM notifications '
                     'JOIN notification_objects ON notifications.entity_id = notification_objects.id '
                     'WHERE receiver_id = ?', [user_id])

    notifications = cur.fetchall()

    return render_template("view_inventory.html", branches=branches, user=user, notifications=notifications)


@bp.route('/delete_notification', methods=['POST'])
def delete_notification():
    """ Deletes notification in database"""
    db = get_db()

    db.execute('DELETE FROM notifications WHERE id = ?', [request.form["id"]])
    db.commit()

    return ('', 204)




