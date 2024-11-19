# app/__init__.py
from flask import Flask, redirect, url_for
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/')
    def root():
        return redirect(url_for('auth.index'))

    return app
