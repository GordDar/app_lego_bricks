from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lego.db' 
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)


from app_lego.models import Order, order_items_table, CatalogItem, Category, AdminUser, Settings, OrderItem


# --- 1. Каталог (GET /catalog) ---
@app.route('/catalog', methods=['GET'])
def get_catalog():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = CatalogItem.query

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                CatalogItem.color.ilike(search_term),
                CatalogItem.description.ilike(search_term)
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [{
        'lot_id': item.lot_id,
        'url': item.url,
        'color': item.color,
        'description': item.description,
        'price': item.price,
        'quantity': item.quantity,
    } for item in pagination.items]

    return jsonify({
        'items': items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

# --- 2. Отправка корзины (POST /cart) ---
@app.route('/cart', methods=['POST'])
def submit_cart():
    data = request.json
    # Ожидается структура:
    # {
    #   "items": [{"id": 1, "quantity": 2}, ...],
    #   "customer_name": "...",
    #   "customer_telephone": "...",
    #   "dostavka": true/false,
    #   "total_price": ...
    # }
    
    items_data = data.get('items')
    customer_name = data.get('customer_name')
    customer_telephone = data.get('customer_telephone')
    dostavka = data.get('dostavka', False)
    total_price = data.get('total_price')
    

    if not items_data or not customer_name or not customer_telephone or total_price is None:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # проверки минимальной суммы заказа
    settings = Settings.query.first()
    if settings and settings.min_order_amount is not None:
        if total_price < settings.min_order_amount:
            return jsonify({
                'error': f'Минимальная сумма заказа составляет {settings.min_order_amount}. '
                         f'Ваш заказ на сумму {total_price} не может быть принят.'
            }), 400


    order = Order(
        customer_name=customer_name,
        customer_telephone=customer_telephone,
        dostavka=dostavka,
        total_price=total_price
    )

    for item in items_data:
        catalog_item_id = item['id']
        quantity_requested = item.get('quantity', 1)
        catalog_item = CatalogItem.query.get(catalog_item_id)
        
        if not catalog_item:
            return jsonify({'error': f'Item with id {catalog_item_id} not found'}), 404
        if catalog_item.quantity < quantity_requested:
            return jsonify({
                'error': f'Недостаточно товара "{catalog_item.description}". '
                         f'Доступно: {catalog_item.quantity}, запрошено: {quantity_requested}'
            }), 400
        
        order_item = OrderItem(
            catalog_item=catalog_item,
            quantity=quantity_requested
        )
        order.items.append(order_item)

        # Обновляем количество на складе после подтверждения заказа
        catalog_item.quantity -= quantity_requested
    
    db.session.add(order)
    db.session.commit()

    return jsonify({'message': 'Order created', 'order_id': order.id})

# --- 3. Логин для админки (POST /admin/login) ---
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = AdminUser.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Logged in'})
    
    return jsonify({'error': 'Invalid credentials'}), 401

# --- 4. Просмотр заказов в админке (GET /admin/orders) ---
@app.route('/admin/orders', methods=['GET'])
@login_required
def get_orders():
    status_filter = request.args.get('status')  # например, 'new', 'completed'
    date_from = request.args.get('date_from')   # формат: 'YYYY-MM-DD'
    date_to = request.args.get('date_to')  
    
    orders_query = Order.query
    

    if status_filter:
        orders_query = orders_query.filter(Order.status == status_filter)
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            orders_query = orders_query.filter(Order.created_at >= date_from_obj)
        except ValueError:
            pass  # некорректный формат даты, можно обработать ошибку
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # добавляем один день, чтобы включить дату окончания
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            orders_query = orders_query.filter(Order.created_at <= date_to_obj)
        except ValueError:
            pass

    orders_query = orders_query.order_by(Order.id.desc())
    
    orders_list = []
    
    for order in orders_query:
        items_list = []
        total_price_order = 0  # Инициализация суммы заказа
        
        for item in order.items:
            catalog_item = item.catalog_item
            price_per_unit = getattr(catalog_item, 'price', 0) 
            
            # Расчет стоимости позиции
            item_total = price_per_unit * item.quantity
            total_price_order += item_total
            
            items_list.append({
                'id': item.id,
                'lot_id': getattr(catalog_item, 'lot_id', None),
                'url': item.url,
                'color': getattr(catalog_item, 'color', None),
                'description': catalog_item.description,
                'quantity_in_order': item.quantity,
                'unit_price': price_per_unit,
                'total_price': item_total,
                'remarks': getattr(item, 'remarks', None)
            })
        
        
        order_total_price = total_price_order
        
        remarks_value = getattr(order, 'remarks', None)
        
        orders_list.append({
            'id': order.id,
            'customer_name': order.customer_name,
            'customer_telephone': order.customer_telephone,
            'dostavka': order.dostavka,
            'total_price': order_total_price,
            'items': items_list,
            'remarks': remarks_value
        })

    return jsonify(orders_list)

# --- 5. Установка курса валют в админке (POST /admin/set_currency) ---
@app.route('/admin/set_currency', methods=['POST'])
@login_required
def set_currency():
    data = request.json
    currency_rate = data.get('currency_rate')  
    
    if currency_rate is None:
        return jsonify({'error': 'Missing currency rate'}), 400
    
    try:
        currency_rate = float(currency_rate)
    except ValueError:
        return jsonify({'error': 'Invalid currency rate'}), 400
    
    
    settings = Settings.query.first()
    if not settings:
        settings = Settings(currency_rate=currency_rate)
        db.session.add(settings)
    else:
        settings.currency_rate = currency_rate
    
    db.session.commit()
    
    return jsonify({'message': 'Currency rate updated', 'currency_rate': settings.currency_rate})

# --- Запуск приложения ---
if __name__ == '__main__':
    app.run(debug=True)