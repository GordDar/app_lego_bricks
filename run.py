from flask import Flask, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app_lego import create_app, create_user
from app_lego.main.routes import main
from app_lego import db


app = create_app()

username_db, password_db = ('привет', '123')





@app.route('/login/<username>&<password>')
def hash_pass(username, password):
    if username==username_db and check_password_hash(generate_password_hash(password), password_db):
        return f'Добро пожаловать в административную панель!'
    else:
        return 'Вход не выполнен!'
            
    

    


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)