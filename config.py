import os

class Config:
    """Application configuration"""
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLite database for user authentication
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB configuration for patient data
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DBNAME = 'stroke_prediction_db'
    
    # Security settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # CSV dataset path
    DATASET_PATH = 'data/healthcare-dataset-stroke-data.csv'
