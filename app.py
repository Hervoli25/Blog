import os
from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from dotenv import load_dotenv
from models import db, User
from flask_login import LoginManager
from livereload import Server

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app and load config
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize CSRF protection
csrf = CSRFProtect(app)
csrf.init_app(app)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-SocketIO
socketio = SocketIO(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'app.login'  # Use 'app.login' to match the blueprint

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Import and register blueprints here to avoid circular imports
from routes import app as app_blueprint
app.register_blueprint(app_blueprint)

if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve()
    socketio.run(app, debug=True)
