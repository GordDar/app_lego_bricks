from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView

# Объявляем расширения без привязки к приложению
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()

# admin = Admin()

def create_app():
    app = Flask(__name__)
    # Загружаем настройки из файла (предположим, что он есть)
    app.config.from_pyfile('main/settings.py')
    
    # Обязательно указываем секретный ключ (можно вынести в настройки)
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    # Настройки базы данных (можно вынести в настройки)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lego.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация расширений с приложением
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    
    migrate.init_app(app, db, render_as_batch=True)
    
    from app_lego.models import Part, Category  

    
    # Регистрация блюпринтов внутри контекста приложения


    return app






if __name__ == '__main__':
    app = create_app()

    app.run(debug=True)