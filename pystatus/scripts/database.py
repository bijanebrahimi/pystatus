# from flask
from werkzeug.security import generate_password_hash, check_password_hash

from pystatus.extensions import db
from pystatus.models import User




def create_db():
    db.create_all()


def user_create(username, email, password):
    user = User(username=username,
                password=generate_password_hash(password),
                email=email)
    db.session.add(user)
    try:
        db.session.commit()
        return user
    except:
        db.session.delete(user)
        return False
