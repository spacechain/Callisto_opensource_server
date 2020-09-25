# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager
import constants


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    state = db.Column(db.Integer, nullable=False, default=constants.USER_ENABLE)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
