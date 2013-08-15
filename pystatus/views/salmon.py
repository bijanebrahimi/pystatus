from flask import Blueprint, render_template, request, abort, make_response
from pystatus.models import User

bp = Blueprint('salmon', __name__, url_prefix='/main/salmon')


@bp.route('/user/', methods=['GET', 'POST'])
def salmon():
    return 'blah'


@bp.route('/user/<user_id>', methods=['GET', 'POST'])
def salmon(user_id):
    print user_id
    print request.form
    return 'blah'
