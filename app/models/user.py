from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.time_utils import utcnow


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default="normal", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    preference_mode = db.Column(db.String(20), default="travel", nullable=False)
    preferred_partners = db.Column(db.JSON, default=list, nullable=False)
    fee_tolerance = db.Column(db.Integer, default=550, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    transactions = db.relationship("Transaction", backref="user", lazy=True)
    recommendation_runs = db.relationship("RecommendationRun", backref="user", lazy=True)
    plan_commits = db.relationship("PlanCommit", backref="user", lazy=True)
    system_events = db.relationship("SystemEvent", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"
