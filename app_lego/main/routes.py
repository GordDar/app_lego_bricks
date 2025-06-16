from flask import render_template, redirect, url_for, request, flash, Request, Blueprint, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from app_lego.models import check_password_hash
from app_lego.models import User
from app_lego.main.forms import LoginForm
from app_lego import db
from datetime import datetime
from app_lego.models import Part, Category


main = Blueprint('main', __name__)


@main.route('/')
def index():
    search = request.args.get('search')
    page = request.args.get('page', 1)
    if page:
        page = int(page)
    else:
        page = 1

    if search:
        parts_query = Part.query.filter(
            Part.description.contains(search) | Part.color.contains(search)
        )
    else:
        parts_query = Part.query.order_by(Part.price)

    pages = parts_query.paginate(page=page, per_page=30)

    return render_template('catalog.html', title='Главная', pages=pages)


@main.route('/condition')
def condition():
    return render_template('condition.html', title = 'Условия покупки')
        


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Вы вошли в аккаунт пользователя {user.username}', 'info')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.account'))
        else:
            flash('Войти не удалось. Пожалуйста, проверьте электронную почту или пароль.', 'danger')
    return render_template('login.html', form=form, title='Авторизация', legend='Войти')


@main.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html', title='Аккаунт', current_user=current_user)


@main.route('/logout')
def logout():
    current_user.last_seen = datetime.now()
    db.session.commit()
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/details')
def details():
    return render_template('details.html', title = 'Каталог')

@main.route('/zakaz')
def zakaz():
    search = request.args.get('search')
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    if search:
        parts = Part.query.filter(Part.description.contains(search) | Part.color.contains(search))
    else:
        parts = Part.query.order_by(Part.price)
    pages = parts.paginate(page = page, per_page = 30)
    return render_template('zakaz.html', title = 'Ваша корзина', pages = pages)

@main.route('/catalog', methods=['GET'])
def catalog():
    search = request.args.get('search')
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    if search:
        parts = Part.query.filter(Part.description.contains(search) | Part.color.contains(search))
    else:
        parts = Part.query.order_by(Part.price)
    pages = parts.paginate(page = page, per_page = 30)
    return render_template('catalog.html', title='Каталог', pages = pages)


@main.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        color = request.form['color']
        description = request.form['description']
        quantity = request.form['quantity']
        category_id = request.form['category_id']
        
        # Преобразование цены в число
        try:
            price_value = float(price)
        except ValueError:
            return "Некорректная цена", 400

        item = Part(name=name, price=price_value, color=color, description=description, quantity=quantity, category_id=category_id)
        
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            # Можно залогировать ошибку
            print(f"Ошибка при добавлении объекта: {e}")
            return 'Произошла ошибка при сохранении объекта!'
    else:
        return render_template('create.html', title='Создание объекта')
    
    
@main.route('/poisk')
def poisk():
    search = request.args.get('search')
    if search:
        parts = Part.query.filter(Part.description.contains(search) | Part.color.contains(search)).all()
    else:
        parts = Part.query.all()
    return render_template('catalog.html', data = parts)


@main.route('/poisk_id')
def poisk_id():
    search_id = request.args.get('search_id')
    if search_id:
        parts = Part.query.filter(Part.id.contains(search_id)).first()
    else:
        parts = Part.query.all()
    return render_template('detail_po_id.html', data = parts)


@main.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('id')
    product_id_str = str(product_id)
    print(f"Adding product ID: {product_id}")  # отладка

    product = Part.query.get(product_id)
    if not product:
        return jsonify({'message': 'Товар не найден'}), 404

    cart = session.get('cart', {})
    if product_id in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.description,
            'price': str(product.price),
            'quantity': 1,
        }
    session['cart'] = cart
    print(f"Current cart: {session['cart']}")  # отладка
    return jsonify({'message': 'Товар добавлен в корзину'})


@main.route('/zakaz')
def cart():
    items = []
    cart = session.get('cart', {})
    for product_id_str, item in cart.items():
        items.append({
            'name': item['name'],
            'price': float(item['price']),
            'quantity': item['quantity'],
            'total': float(item['price']) * item['quantity']
    })
    return render_template('zakaz.html', items=items, total_price=sum(i['total'] for i in items))


@main.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect('/zakaz')


@main.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    products = Part.query.filter_by(category_id=category.id).all()
    return render_template('products.html', products=products, category=category)






            
            
    
# @app.route('/.')
# def home():
    # categories = Category.query.all()
    # parts = Part.query.all()
    # return render_template('index.html', categories=categories, parts=parts)

# @app.route('/product/<int:part_id>')
# def product_detail(part_id):
#     part = Part.query.get_or_404(part_id)
#     return render_template('product.html', part=part)

# @app.route('/add_to_cart/<int:part_id>')
# def add_to_cart(part_id):
#     cart = session.get('cart', {})
#     cart[str(part_id)] = cart.get(str(part_id), 0) + 1
#     session['cart'] = cart
#     return redirect(url_for('index'))

# @app.route('/cart')
# def view_cart():
#     cart = session.get('cart', {})
#     parts_in_cart = []
#     total_price = 0

#     for part_id_str, quantity in cart.items():
#         part = Part.query.get(int(part_id_str))
#         if part:
#             item_total = part.price * quantity
#             total_price += item_total
#             parts_in_cart.append({'part': part, 'quantity': quantity, 'total': item_total})

#     return render_template('cart.html', cart=parts_in_cart, total_price=total_price)

# @app.route('/clear_cart')
# def clear_cart():
#     session.pop('cart', None)
#     return redirect(url_for('view_cart'))