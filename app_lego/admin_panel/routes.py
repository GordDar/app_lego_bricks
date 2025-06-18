from flask import render_template, redirect, url_for, request, flash, Request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app_lego.models import check_password_hash
from app_lego.models import User
from app_lego.admin_panel.forms import LoginForm
from app_lego import db
from datetime import datetime
from app_lego.models import Part, Category, User



admin_panel = Blueprint('admin_panel', __name__)

@admin_panel.route('/admin_panel')
def index():
    return render_template('admin_panel/spisok_zakazov.html', title='Панель администратора')
        


@admin_panel.route('/admin_panel/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_panel.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Вы вошли в аккаунт пользователя {user.username}', 'info')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_panel.index'))
        else:
            flash('Войти не удалось. Пожалуйста, проверьте электронную почту или пароль.', 'danger')
    return render_template('admin_panel/login.html', form=form, title='Авторизация', legend='Войти')


@admin_panel.route('/admin_panel/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('admin_panel/account.html', title='Аккаунт', current_user=current_user)


@admin_panel.route('/admin_panel/logout')
def logout():
    current_user.last_seen = datetime.now()
    db.session.commit()
    logout_user()
    return redirect(url_for('admin_panel.index'))



@admin_panel.route('/admin_panel/spisok_zakazov')
def zakaz():
    
    return render_template('admin_panel/spisok_zakazov.html', title = 'Ваша корзина')


@admin_panel.route('/admin_panel/catalog', methods=['GET'])
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
    return render_template('admin_panel/catalog.html', title='Каталог', pages = pages)


@admin_panel.route('/admin_panel/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        lot_id = request.form['lot_id']
        price = request.form['price']
        color = request.form['color']
        description = request.form['description']
        quantity = request.form['quantity']
        category_id = request.form['category_id']
        remarks = request.form['remarks']
        
        # Преобразование цены в число
        try:
            price_value = float(price)
        except ValueError:
            return "Некорректная цена", 400

        item = Part(lot_id = lot_id, price=price_value, color=color, description=description, quantity=quantity, category=category_id, remarks=remarks)
        
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/admin_panel')
        except Exception as e:
            # Можно залогировать ошибку
            print(f"Ошибка при добавлении объекта: {e}")
            return 'Произошла ошибка при сохранении объекта!'
    else:
        return render_template('admin_panel/create.html', title='Создание объекта')
    
