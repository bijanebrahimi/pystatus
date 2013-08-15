from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

__all__ = ['db', 'mail']

db = SQLAlchemy()
mail = Mail()
