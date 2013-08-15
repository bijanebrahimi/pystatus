from flask import Blueprint, render_template, request, abort, make_response
from pystatus.models import User

bp = Blueprint('activitystreams', __name__, url_prefix='/main/activitystreams')

@bp.route('/user_timeline/<user_id>.atom', methods=['GET'])
def user_timeline(user_id):
    print 'activity stream'
    user = User.query.filter(User.id==user_id).first_or_404()
    
    response= make_response(render_template('activitystreams/user_timeline.xml',
                                            user=user))
    response.headers['Content-Type'] = 'application/xml'
    return response
