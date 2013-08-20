from flask import Blueprint, render_template, request, abort, make_response
from pystatus.models import User
from pystatus.libs import MagicSig, AtomFeed

bp = Blueprint('salmon', __name__, url_prefix='/main/salmon')


@bp.route('/user/', methods=['POST'])
def salmon():
    return 'blah'


@bp.route('/user/<user_id>', methods=['POST'])
def salmon(user_id):
    magicsig = MagicSig(request.data)
    atom = AtomFeed(magicsig.data_decoded)
    print atom.atom
    return ''
