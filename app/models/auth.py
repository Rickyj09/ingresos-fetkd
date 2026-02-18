from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager
from app.models.base import TimestampMixin

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)  # ADMIN, OPERADOR, CONSULTA

class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", backref=db.backref("users", lazy=True))

    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))