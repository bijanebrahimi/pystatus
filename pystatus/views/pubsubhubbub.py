from flask import Blueprint, render_template, request, abort, make_response
from pystatus.models import User

bp = Blueprint('push', __name__, url_prefix='/main/push')


@bp.route('/', methods=['POST'])
def push():
    response= make_response(render_template('webfinger/host-meta.xml'))
    response.headers['Content-Type'] = 'application/xrd+xml'
    return response
