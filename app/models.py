from flask_login import UserMixin
from flask import current_app
from app import login_manager
from app.ApiSettingsDB import ApiSettingsDB


class User(UserMixin):
    def __init__(self, user_id, username, password_hash):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash

    def get_user_id(self):
        return self.id


@login_manager .user_loader
def load_user(user_id):
    with ApiSettingsDB(current_app.config) as db:
        user_info = db.get_user_by_id(user_id)

    if user_info is not None:
        user = User(user_id=user_info[0], username=user_info[1], password_hash=user_info[2])
    else:
        user = None

    return user
