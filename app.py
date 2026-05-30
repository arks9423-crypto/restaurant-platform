from flask import Flask
from models import db, SuperAdmin
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    @app.context_processor
    def inject_config():
        return {"config": app.config}

    with app.app_context():
        db.create_all()
        _migrate_db(db)
        _seed_super_admin(app)

    from routes.platform import platform_bp
    from routes.super_admin import super_admin_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.menu import menu_bp
    from routes.orders import orders_bp

    app.register_blueprint(platform_bp)
    app.register_blueprint(super_admin_bp, url_prefix="/platform")
    app.register_blueprint(auth_bp, url_prefix="/r/<slug>")
    app.register_blueprint(admin_bp, url_prefix="/r/<slug>")
    app.register_blueprint(menu_bp, url_prefix="/r/<slug>")
    app.register_blueprint(orders_bp, url_prefix="/r/<slug>")

    return app


def _migrate_db(db):
    migrations = [
        "ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS email VARCHAR(120)",
        "ALTER TABLE restaurant ADD COLUMN IF NOT EXISTS logo_data TEXT",
    ]
    for sql in migrations:
        with db.engine.connect() as conn:
            try:
                conn.execute(db.text(sql))
                conn.commit()
            except Exception:
                pass


def _seed_super_admin(app):
    if SuperAdmin.query.count() == 0:
        sa = SuperAdmin(username=app.config["SUPER_ADMIN_USERNAME"])
        sa.set_password(app.config["SUPER_ADMIN_PASSWORD"])
        db.session.add(sa)
        db.session.commit()
