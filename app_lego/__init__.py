from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Объявляем расширения без привязки к приложению
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
admin = Admin()

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
    admin.init_app(app)
    
    migrate.init_app(app, db, render_as_batch=True)
    
    from app_lego.models import Part, Category  
    admin.add_view(ModelView(Part, db.session))
    admin.add_view(ModelView(Category, db.session))
    
    # Регистрация блюпринтов внутри контекста приложения
    with app.app_context():
        from app_lego.main.routes import main as main_blueprint
        from app_lego.user.routes import users as users_blueprint
        from app_lego.part.routes import parts as parts_blueprint

        app.register_blueprint(main_blueprint)
        app.register_blueprint(users_blueprint)
        app.register_blueprint(parts_blueprint)

    return app

def create_user():
    with create_app().app_context():
        from app_lego.models import User
        db.drop_all()
        db.create_all()

        hashed_password = bcrypt.generate_password_hash('123').decode('utf-8')
        user= User(username='привет', email='admin@m.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    create_user()
    app.run(debug=True)
        
        

        
        