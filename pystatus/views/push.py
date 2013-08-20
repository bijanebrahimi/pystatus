import urllib
import urlparse
from flask import Blueprint, render_template, request, abort, make_response
from pystatus.models import User, Subscriber
from pystatus.extensions import db

bp = Blueprint('push', __name__, url_prefix='/main/push')


def verify_subscription(callback, params):
    params['challenge'] = 'someRandomText'
    url_parts = list(urlparse.urlparse(callback))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    verification_request = urlparse.urlunparse(url_parts)
    
    verification_response = urllib.urlopen(verification_request).read()
    print '===========check================'
    print 'challenging %s' % verification_request
    print 'response:', verification_response
    print 'challenge: %s' % params['challenge']
    # FIXME: for unsubscribe is it neccessary?'
    # if verification_response == params['challenge']:
    return True


@bp.route('/hub', methods=['POST', 'GET'])
def push():
    print request.form
    # TODO: sanity checks
    if request.form['hub.mode'] == 'subscribe':
        # TODO: renewal check
        if request.form['hub.verify'] == 'sync':
            verification_params = {'hub.mode': 'subscribe',
                                   'hub.topic': request.form['hub.topic'],
                                   'hub.lease_seconds': '60',
                                   'hub.verify_token': request.form['hub.verify_token']}
            if verify_subscription(request.form['hub.callback'], verification_params):
                subscriber = Subscriber(topic=request.form['hub.topic'],
                                        callback=request.form['hub.callback'],
                                        secret=request.form['hub.secret'],
                                        verify=request.form['hub.verify'],
                                        verify_token=request.form['hub.verify_token'])
                db.session.add(subscriber)
                db.session.commit()
                return ''
        elif request.form['hub.verify'] == 'async':
            pass
    elif request.form['hub.mode'] == 'unsubscribe':
        subscriber = Subscriber.query.filter(Subscriber.topic==request.form['hub.topic'],
                                             Subscriber.callback==request.form['hub.callback']).first_or_404()
        if request.form['hub.verify'] == 'sync':
            verification_params = {'hub.mode': 'unsubscribe',
                                   'hub.topic': request.form['hub.topic'],
                                   'hub.verify_token': request.form['hub.verify_token']}
            if verify_subscription(request.form['hub.callback'], verification_params):
                db.session.delete(subscriber)
                db.session.commit()
                abort(204)
        elif request.form['hub.verify'] == 'async':
            pass
    # TODO: remover subscriber?
    abort(405)


@bp.route('/sub/<uri>', methods=['POST', 'GET'])
def sub(uri):
    print 'sub'
    print request.form
    abort(404)
