import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'yamora-retails-super-secret-key-2026')
    
    # Production Environment
    ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    # Security Cookie Options
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    if os.environ.get('SECURE_COOKIES', 'false').lower() == 'true':
        SESSION_COOKIE_SECURE = True
        REMEMBER_COOKIE_SECURE = True
    
    # MySQL Connection Parameters
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'yamoraretails_db')

    # Default to SQLite for zero-config execution if USE_MYSQL != 'true'
    USE_MYSQL = os.environ.get('USE_MYSQL', 'false').lower() == 'true'
    
    if USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    else:
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'yamoraretails.db')}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
