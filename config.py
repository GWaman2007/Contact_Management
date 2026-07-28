import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SQLite Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', f"sqlite:///{os.path.join(BASE_DIR, 'contacts.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security Keys (Minimum 32 bytes for secure HMAC)
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-contacts-store-app-key-32bytes-long!')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-token-authentication-key-32bytes!')

    # File Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB Max Upload Size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
