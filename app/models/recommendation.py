from uuid import uuid4

from app.extensions import db
from app.time_utils import utcnow


class RecommendationRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    run_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()), nullable=False)
    preferences_snapshot = db.Column(db.JSON)
    results = db.Column(db.JSON)
    top_card_id = db.Column(db.String(50))
    total_estimated_value = db.Column(db.Float)
    cpp_assumption = db.Column(db.Float, default=1.5)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
