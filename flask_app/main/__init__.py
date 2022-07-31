from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app(ENV):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'splitwise'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if ENV == 'dev':
        app.debug = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/group-expences-manager'
    else:
        app.debug = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app