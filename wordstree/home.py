from flask import (
    Blueprint, render_template, current_app
)

from wordstree.db import get_db

bp = Blueprint('root', __name__)


@bp.route('/')
def home():
    """ Handles requests to the root page """
    return render_template('home.html')


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')
