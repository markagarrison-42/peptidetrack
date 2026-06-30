from flask import Flask
from extensions import db, login_manager, mail
import os
import urllib.parse


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")

    # Database
    db_host = os.environ.get("DB_HOST")
    if db_host:
        db_pass = urllib.parse.quote_plus(os.environ.get("DB_PASS", ""))
        db_user = os.environ.get("DB_USER", "")
        db_name = os.environ.get("DB_NAME", "")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}?charset=utf8mb4"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///peptidetrack.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 280,
    "pool_pre_ping": True,
}

    # Mail
    app.config["MAIL_SERVER"]         = "smtp.gmail.com"
    app.config["MAIL_PORT"]           = 587
    app.config["MAIL_USE_TLS"]        = True
    app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USER")
    app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASS")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USER")

    # Cloudinary
    app.config["CLOUDINARY_URL"] = os.environ.get("CLOUDINARY_URL")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    mail.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from routes.main       import main_bp
    from routes.auth       import auth_bp
    from routes.patients   import patients_bp
    from routes.compounds  import compounds_bp
    from routes.protocols  import protocols_bp
    from routes.checkins   import checkins_bp
    from routes.doses      import doses_bp
    from routes.labs       import labs_bp
    from routes.photos     import photos_bp
    from routes.profile    import profile_bp
    from routes.push       import push_bp
    from routes.learn      import learn_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,       url_prefix="/auth")
    app.register_blueprint(patients_bp,   url_prefix="/api/patients")
    app.register_blueprint(compounds_bp,  url_prefix="/api/compounds")
    app.register_blueprint(protocols_bp,  url_prefix="/api/protocols")
    app.register_blueprint(checkins_bp,   url_prefix="/api/checkins")
    app.register_blueprint(doses_bp,      url_prefix="/api/doses")
    app.register_blueprint(labs_bp,       url_prefix="/api/labs")
    app.register_blueprint(photos_bp,     url_prefix="/api/photos")
    app.register_blueprint(profile_bp,    url_prefix="/api/profile")
    app.register_blueprint(push_bp,       url_prefix="/api/push")
    app.register_blueprint(learn_bp,      url_prefix="/api/learn")

    with app.app_context():
        db.create_all()

    return app


application = create_app()

from flask import render_template

@application.route('/moved')
def moved():
    return render_template('moved.html')