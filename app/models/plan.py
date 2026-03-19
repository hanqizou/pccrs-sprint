from uuid import uuid4

from app.extensions import db
from app.time_utils import utcnow


class PlanCommit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    txn_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()), nullable=False)
    rec_run_id = db.Column(db.String(36), db.ForeignKey("recommendation_run.run_id"))
    action = db.Column(db.String(10), nullable=False)
    card_ids = db.Column(db.JSON, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
