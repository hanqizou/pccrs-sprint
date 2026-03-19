from app.routes.admin import admin_bp
from app.routes.analysis import analysis_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.history import history_bp
from app.routes.ingestion import ingestion_bp
from app.routes.plan import plan_bp
from app.routes.reporting import reporting_bp

ALL_BLUEPRINTS = [
    auth_bp,
    dashboard_bp,
    ingestion_bp,
    analysis_bp,
    plan_bp,
    history_bp,
    reporting_bp,
    admin_bp,
]

