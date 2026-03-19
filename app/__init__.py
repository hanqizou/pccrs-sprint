import os
import sys

from flask import Flask

from app.config import get_config_class
from app.extensions import csrf, db, login_manager, migrate
from app.models import User
from app.routes import ALL_BLUEPRINTS


def should_create_tables():
    if os.getenv("SKIP_DB_CREATE", "0") == "1":
        return False

    return "db" not in sys.argv[1:]


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config_class())

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

    if should_create_tables():
        with app.app_context():
            db.create_all()

    return app
