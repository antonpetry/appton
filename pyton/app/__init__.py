from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from config import Config

db = SQLAlchemy()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from .routes.main import main_bp
    from .routes.weight import weight_bp
    from .routes.nutrition import nutrition_bp
    from .routes.training import training_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(weight_bp, url_prefix="/weight")
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(training_bp)

    with app.app_context():
        from .models.weight import WeightEntry
        db.create_all()

    return app
