from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'  
login_manager.login_message = '请先登录以访问该页面'
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()
        from .models import Major, User
        if not Major.query.first():
            db.session.add_all([
                Major(major_name='计算机科学与技术'),
                Major(major_name='软件工程')
            ])
            db.session.commit()

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')  # 原代码的初始密码
            db.session.add(admin)
            db.session.commit()

    return app