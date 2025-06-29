from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from app_lego.models import AdminUser
from flask import flash


class RegistarionForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('Емейл', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Войти')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data)
        if user:
            flash('Это имя уже занято. Пожалуйста, выберите другое.', 'danger')
            raise ValidationError('That username is taken. Please, choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            flash('Этот емейл уже занят. Пожалуйста, введите другой.', 'danger')
            raise ValidationError('That email is taken. Please, choose a different one.')
        
        
class LoginForm(FlaskForm):
    email = StringField('Емейл', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')