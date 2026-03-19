from app.extensions import db
from app.time_utils import utcnow


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    import_id = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    merchant = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False)
    original_amount = db.Column(db.Float)
    original_currency = db.Column(db.String(3), default="USD")
    category = db.Column(db.String(50), nullable=False)
    mcc_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
