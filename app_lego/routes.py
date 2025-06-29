from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from datetime import datetime
from app_lego import db
from app_lego.models import Order, CatalogItem, Category, AdminUser, Settings, OrderItem

app = Flask(__name__)

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
        'category': item.category.name if item.category else None
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
    # Структура:
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
    
    # Проверка минимальной суммы заказа
    settings = Settings.query.filter_by(settings_name='минимальная сумма заказа').first()
    min_order_amount = settings.settings_value if settings else None
    
    if min_order_amount is not None:
        if total_price < min_order_amount:
            return jsonify({
                'error': f'Минимальная сумма заказа составляет {min_order_amount}. '
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
        order.order_items.append(order_item)

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
    status_filter = request.args.get('status')  # например: 'new', 'completed'
    date_from_str = request.args.get('date_from')   # формат: 'YYYY-MM-DD'
    date_to_str = request.args.get('date_to')  
    
    orders_query = Order.query.all()


    
    if status_filter:
        orders_query = orders_query.filter(Order.status == status_filter)
        
    if date_from_str:
        try:
            date_from_obj = datetime.strptime(date_from_str, '%Y-%m-%d')
            orders_query = orders_query.filter(Order.created_at >= date_from_obj)
        except ValueError:
            pass
    
    if date_to_str:
        try:
            date_to_obj = datetime.strptime(date_to_str, '%Y-%m-%d')
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            orders_query = orders_query.filter(Order.created_at <= date_to_obj)
        except ValueError:
            pass

    orders_query = orders_query.order_by(Order.id.desc())

    orders_list=[]
    
    for order in orders_query.all():
        items_list=[]
        total_order_price=0

        for item in order.order_items:
            catalog_item=item.catalog_item
            price_per_unit=getattr(catalog_item,'price',0)
            qty=item.quantity
            item_total=price_per_unit*qty
            total_order_price+=item_total

            items_list.append({
                'id': catalog_item.id,
                'lot_id': catalog_item.lot_id,
                'url': catalog_item.url,
                'color': catalog_item.color,
                'description': catalog_item.description,
                'quantity_in_order': qty,
                'unit_price': price_per_unit,
                'total_price': item_total,
                "remarks": getattr(catalog_item,'remarks',None)
            })

        remarks_value=getattr(order,'remarks',None)

        orders_list.append({
            'id': order.id,
            'customer_name': order.customer_name,
            'customer_telephone': order.customer_telephone,
            'dostavka': order.dostavka,
            'total_price': total_order_price,
            'items': items_list,
            "remarks": remarks_value
        })

    return jsonify(orders_list)

# --- 5. Установка курса валют в админке (POST /admin/set_currency) ---
def create_initial_settings():
    initial_settings=[
        {'settings_name':'курс белорусского рубля','settings_value':0},
        {'settings_name':'курс российского рубля','settings_value':0},
        {'settings_name':'минимальная сумма заказа','settings_value':0}
    ]
    for setting in initial_settings:
        existing=Settings.query.filter_by(settings_name=setting['settings_name']).first()
        if not existing:
            new_setting=Settings(
                settings_name=setting['settings_name'],
                settings_value=setting['settings_value']
            )
            db.session.add(new_setting)
    db.session.commit()

@app.route('/admin/set_currency', methods=['POST'])
@login_required
def update_settings():
    data=request.get_json()
    for key,value_set in data.items():
        value=next(iter(value_set),None) if isinstance(value_set,set) else value_set

        if value is not None:
            setting=Settings.query.filter_by(settings_name=key).first()
            if setting:
                if value != '' and value is not None:
                    setting.settings_value=float(value)
    try:
        db.session.commit()
        return jsonify({"status":"success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status":"error","message":str(e)})

# --- 6. Структура категорий ---
def build_nested_structure(paths):
    structure={}
    for path in paths:
        parts=[part.strip() for part in path.split('/')]
        current_level=structure
        for i,part in enumerate(parts):
            if i==len(parts)-1:
                current_level[part]=current_level.get(part,{})
            else:
                if part not in current_level:
                    current_level[part]={}
                current_level=current_level[part]
    return structure

@app.route("/category-structure")
def get_category_structure():
    categories=[item.category.name for item in CatalogItem.query.all() if item.category]
    nested_structure=build_nested_structure(categories)
    return jsonify(nested_structure)



# --- 7. Просмотр одного заказа из админки ---
@app.route('/admin/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order=Order.query.filter(Order.id==order_id).first()
    if not order:
        abort(404,"Order not found")
    
    items_list=[]
    total_order_price=0

    for item in order.order_items:
        catalog_item=item.catalog_item
        price_per_unit=catalog_item.price if catalog_item else 0
        qty=item.quantity
        item_total=price_per_unit*qty
        total_order_price+=item_total

        items_list.append({
            "id":catalog_item.id,
            "lot_id":catalog_item.lot_id,
            "url":catalog_item.url,
            "color":catalog_item.color,
            "description":catalog_item.description,
            "quantity_in_order":qty,
            "unit_price":price_per_unit,
            "total_price":item_total,
            "remarks":getattr(catalog_item,'remarks',None)
        })

    response_data={
        "id":order.id,
        "customer_name":order.customer_name,
        "customer_telephone":order.customer_telephone,
        "dostavka":order.dostavka,
        "total_price":total_order_price,
        "items":items_list
    }

    return jsonify(response_data)

# --- 8. Просмотр данных по одной детали ---
@app.route('/catalog_item/<int:item_id>', methods=['GET'])
def get_catalog_item(item_id):
    item=CatalogItem.query.get(item_id)
    if item:
        return jsonify({
            'lot_id': item.lot_id,
            'color': item.color,
            'category': item.category,
            'condition': item.condition,
            'description': item.description,
            'price': item.price,
            'quantity': item.quantity,
            'url': item.url,
            'currency': item.currency
        })
    else:
        abort(404, description="Item not found")

