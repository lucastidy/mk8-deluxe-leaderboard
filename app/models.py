from . import db, login_manager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# user model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# leaderboard entry model
class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True) #SHOULD THIS BE user_id?
    track = db.Column(db.String(100), nullable=False)
    time_mins = db.Column(db.Integer, nullable=False)
    time_s = db.Column(db.Integer, nullable=False)
    time_ms = db.Column(db.Integer, nullable=False)

    #link to a user
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="scores")

    screenshot_path = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False)
