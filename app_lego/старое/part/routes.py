from flask import render_template, redirect, url_for, request, flash, Request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app_lego.models import check_password_hash
from app_lego.models import User
from app_lego.main.forms import LoginForm
from app_lego import db
from datetime import datetime

parts = Blueprint('parts', __name__)


# @parts.route('/part/<int:part_id>')
# def part():
#     part= Part.query.get_or_404(part_id)
#     return render_template('part.html', title = 'Детали')


        



