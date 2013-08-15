# from flask
from werkzeug.security import generate_password_hash, check_password_hash

from pystatus.extensions import db
from pystatus.models import User




def create_db():
    db.create_all()


def user_create(nickname, email, password):
    user = User(nickname=nickname,
                password=generate_password_hash(password),
                email=email)
    db.session.add(user)
    try:
        db.session.commit()
        return user
    except:
        db.session.delete(user_entity)
        return False
