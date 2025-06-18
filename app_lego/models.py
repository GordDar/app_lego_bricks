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

    parts = db.relationship('Part', backref='category_obj')

class Part(db.Model):
    __tablename__ = 'part'
    __searchable__ = ['color', 'description']


    

    id = db.Column(db.Integer, primary_key=True)  # уникальный идентификатор записи (может быть автоинкремент)
    lot_id = db.Column(db.String(50), nullable=False)  
    color = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(100), db.ForeignKey('category.name'), nullable=False)
    condition = db.Column(db.String(50))
    sub_condition = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    remarks = db.Column(db.Text)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    bulk = db.Column(db.Boolean)
    sale = db.Column(db.Boolean)
    url = db.Column(db.String(255))
    item_no = db.Column(db.String(50))
    tier_qty_1 = db.Column(db.Integer)
    tier_price_1 = db.Column(db.Float)
    tier_qty_2 = db.Column(db.Integer)
    tier_price_2 = db.Column(db.Float)
    tier_qty_3 = db.Column(db.Integer)
    tier_price_3 = db.Column(db.Float)
    reserved_for = db.Column(db.String(100))
    stockroom = db.Column(db.String(100))
    retain = db.Column(db.Boolean)
    super_lot_id = db.Column(db.String(50))
    super_lot_qty = db.Column(db.Integer)
    weight = db.Column(db.Float)
    extended_description = db.Column(db.Text)
    date_added = db.Column(db.DateTime)
    date_last_sold = db.Column(db.DateTime)
    currency = db.Column(db.String(10))