from flask import render_template, redirect, url_for, request, flash, Request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import check_password_hash, generate_password_hash
from app_lego.models import AdminUser
from app_lego.user.forms import RegistarionForm
from app_lego import db


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistarionForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode('utf-8')
        user = AdminUser(username=form.username.data, email=form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # full_path = os.path.join(os, getcwd(), 'app_lego/static', 'profile_pics', user.username)
        # if not os.path.exists(full_path):
        #     os.mkdir(full_path)
        # shutil.copy(f'{os.getcwd()}/app_lego/static/profile_pics/default.jpg', full_path)
        flash(' Ваш аккаунт был создан. Вы можете войти.', 'success')
        
        return redirect(url_for('main.login'))
    return render_template('registration.html', form = form, title = 'Регистрация', legend='Регистрация')

# @main.route('/condition')
# def condition():
#     return render_template('condition.html', title = 'Условия покупки')
        


# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))    
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and check_password_hash(user.password, form.password.data):
#             login_user(user, remember=form.remember.data)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('main.account'))
#         else:
#             flash('Войти не удалось. Пожалуйстаб проверьте электронную почту или пароль.', 'danger')
#     return render_template('login.html', form=form, title='Авторизация', legend='Войти')


# @main.route('/account', methods=['GET', 'POST'])
# @login_required
# def account():
#     return render_template('account.html', title='Аккаунт', current_user=current_user)


# @main.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('main.index'))

# @main.route('/details')
# def details():
#     return render_template('details.html', title = 'Каталог')