from app_lego import db, login_manager, bcrypt
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # увеличил длину для хранения хеша
    
    # пример связи (раскомментировать при необходимости)
    # zakazi = db.relationship('Part', backref='zakazal', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'User({self.username}, {self.email})'


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    parts = db.relationship('Part', backref='category', lazy=True)

class Part(db.Model):
    __tablename__ = 'part'
    __searchable__ = ['color', 'description']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    isNew = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)