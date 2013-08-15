from flask import Blueprint, render_template, request, abort, make_response
from pystatus.models import User

bp = Blueprint('webfinger', __name__)


@bp.route('/.well-known/host-meta', methods=['GET'])
def webfinger_hostmeta():
    response= make_response(render_template('webfinger/host-meta.xml'))
    response.headers['Content-Type'] = 'application/xrd+xml'
    return response


@bp.route("/main/xrd/<uri>", methods=['GET'])
def webfinger_xrd(uri):
    try:
        (nickname, host) = uri.replace(r"acct:", "").split("@")
        user = User.query.filter(User.nickname==nickname).first_or_404()
        response= make_response(render_template('webfinger/xrd.xml', user=user))
        response.headers['Content-Type'] = 'application/xrd+xml'
        return response
    except:
        abort(503)
