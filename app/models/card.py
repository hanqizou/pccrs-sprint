from app.extensions import db
from app.time_utils import utcnow


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    issuer = db.Column(db.String(50))
    annual_fee = db.Column(db.Float, default=0)
    base_reward_rate = db.Column(db.Float, default=1.0)
    category_multipliers = db.Column(db.JSON, default=dict, nullable=False)
    credits = db.Column(db.JSON, default=dict, nullable=False)
    credit_utilization_rate = db.Column(db.Float, default=0.8)
    transfer_partners = db.Column(db.JSON, default=dict, nullable=False)
    category_caps = db.Column(db.JSON, default=dict, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=utcnow)
