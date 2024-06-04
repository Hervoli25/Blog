#from flask import Flask
from flask_migrate import Migrate
from models import db
from routes import app
from flask_wtf.csrf import CSRFProtect
from livereload import Server
from dotenv import load_dotenv
import os

csrf = CSRFProtect(app)  # Ensure this line is present and correct
csrf.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == "__main__":
    server = Server(app.wsgi_app)
    app.run(debug=True)
