from flask import Flask, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app_lego import create_app, create_user
from app_lego.main.routes import main
from app_lego import db
from app_lego import create_initial_settings


app = create_app()



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_initial_settings()
        app.run(debug=True)