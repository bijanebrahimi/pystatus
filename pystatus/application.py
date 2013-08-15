from flask import Flask
from pystatus.config import DevelopmentConfig as default_config
from pystatus.extensions import db, mail

__all__ = ['create_app']


def create_app(config=default_config):
    """
    create actual app object and configure it
    """
    app = Flask(__name__)

    configure_app(app, config)
    configure_sqlalchemy(app)
    # configure_email(app)
    configure_folders(app)
    configure_blueprints(app)
    # configure_i18n(app)
    # configure_errorhandlers(app)
    # configure_before_requests(app)
    # configure_after_requests(app)
    return app


def configure_app(app, config):
    app.config.from_object(default_config())
    if config is not None:
        app.config.from_object(config)
    app.config.from_envvar('project_CONFIG', silent=True)


def configure_sqlalchemy(app):
    db.init_app(app)
    db.app = app


def configure_blueprints(app):
    # TODO: FIX dynamic imports
    from pystatus.views import webfinger, activitystreams, push, salmon
    app.register_blueprint(webfinger.bp)
    app.register_blueprint(activitystreams.bp)
    app.register_blueprint(push.bp)
    app.register_blueprint(salmon.bp)
    # app.register_blueprint(bookmark.bp)
    # app.register_blueprint(comment.bp)
    pass


def configure_folders(app):
    BASE_DIR = app.config['BASE_DIR']
    app.template_folder = BASE_DIR + '/templates'
    # app.static_folder = BASE_DIR + '/media/static'
