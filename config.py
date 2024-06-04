# App Configuration
import os
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '22228c11b19a2a15dafe767d6489496dea822008960c504746f1594616c338aa')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres2@localhost/blog')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
    MAX_CONTENT_PATH = 1000000
    WTF_CSRF_ENABLED = True


