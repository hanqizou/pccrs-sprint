from app.extensions import db
from app.time_utils import utcnow


class SystemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    event_type = db.Column(db.String(30), nullable=False)
    summary = db.Column(db.String(500))
    details = db.Column(db.JSON)
    status = db.Column(db.String(10), default="success", nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
