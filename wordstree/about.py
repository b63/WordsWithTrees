from wordstree.db import get_db
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session

from .services import render_service

bp = Blueprint('about', __name__)

@bp.route('/about', methods=['GET'])
def get_about():
    """display about page"""
    if session.get('user_id') is None:
        return redirect(url_for('login.login_as_get'))

    db = get_db()
    user_id = session['user_id']

    # get user's name and token amount
    cur = db.execute('SELECT name, token FROM users WHERE id = ?', [user_id])
    user = cur.fetchone()

    return render_template('about.html', user=user)
