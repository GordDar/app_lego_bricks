from app_lego.__init__старый import db, login_manager, bcrypt
from flask_bcrypt import check_password_hash, generate_password_hash


# Таблица связи "многие ко многим" между заказами и товарами
# order_items_table = db.Table('order_items',
#     db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
#     db.Column('catalog_item_id', db.Integer, db.ForeignKey('catalog_item.id'), primary_key=True),
#     db.Column('quantity', db.Integer, nullable=False, default=1)  # Количество товара в заказе
# )

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    catalog_item_id = db.Column(db.Integer, db.ForeignKey('catalog_item.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', back_populates='items')
    catalog_item = db.relationship('CatalogItem')

# Модель "Заказы"
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    customer_telephone = db.Column(db.String(20))
    dostavka = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Float)
    # Связь с товарами через таблицу many-to-many
    items = db.relationship('CatalogItem', secondary='order_items', back_populates='orders')


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    settings_name = db.Column(db.String(20))
    settings_value = db.Column(db.Float)
    

@login_manager.user_loader
def load_user(user_id):
   return AdminUser.query.get(int(user_id))

# Модель "Админ пользователи"
class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer)
    name = db.Column(db.String(100), unique=True, primary_key=True, nullable=False)
    
    # Связь с товарами
    catalog_items = db.relationship('CatalogItem', backref='category', lazy=True)

    # Альтернативная связь (если нужна)
    parts = db.relationship('CatalogItem', backref='category_obj')


class CatalogItem(db.Model):
    __tablename__ = 'catalog_item'
    __searchable__ = ['color', 'description']

    id = db.Column(db.Integer, primary_key=True)  # уникальный идентификатор записи (может быть автоинкремент)
    
    lot_id = db.Column(db.String(50), nullable=False)  
    color = db.Column(db.String(20), nullable=False)
    
    # Внешний ключ на категорию по имени (рекомендуется использовать id для надежности)
    category = db.Column(db.Integer, db.ForeignKey('category.name'), nullable=False)
    
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
    
   # Валюта
    currency = db.Column(db.String(10))
   
   # Связь с заказами через таблицу many-to-many
    orders=db.relationship('Order', secondary='order_items', back_populates='items')