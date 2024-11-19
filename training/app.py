# app.py
from flask import Flask, session
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.secret_key = 'you-will-never-guess'  # Secret key for session management
    app.run(debug=True)
