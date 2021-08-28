from flask import Blueprint, render_template


bp = Blueprint('main_data', __name__)


@bp.route('/')
def index():
    return render_template('index.html')
