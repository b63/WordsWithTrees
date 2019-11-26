from wordstree.db import get_db
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session

bp = Blueprint('sell', __name__)

@bp.route('/sell', methods=['GET'])
def sell_branches_get():
    pass
