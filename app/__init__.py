from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import *

login_manager = LoginManager()
mail = Mail()
def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object("app.secure")
    register_blueprint(app)

    login_manager.init_app(app)
    login_manager.login_view = "http://www.baidu.com"
    login_manager.login_message = "请先登录或注册"

    mail.init_app(app)

    return app


def register_blueprint(app):
    from app.web import web
    app.register_blueprint(web)
