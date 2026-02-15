"""
Configuration settings for Smart Office Monitoring System
"""
import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'office_monitoring.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'face_data')
    TRAINED_MODELS_FOLDER = os.path.join(BASE_DIR, 'trained_models')
    
    # Admin credentials (change in production)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    
    # Camera settings
    CAMERA_INDEX = 0  # Default webcam
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Detection settings
    FACE_DETECTION_SCALE_FACTOR = 1.1
    FACE_DETECTION_MIN_NEIGHBORS = 5
    FACE_DETECTION_MIN_SIZE = (30, 30)
    
    # Recognition settings
    RECOGNITION_CONFIDENCE_THRESHOLD = 70  # Lower is more confident (0-100)
    FACE_RECOGNITION_TOLERANCE = 0.6
    ENTRY_EXIT_COOLDOWN_MINUTES = 5  # Prevent duplicate entries within this time
    
    # Training settings
    FACE_SAMPLES_PER_EMPLOYEE = 50
    
    # Ensure required directories exist
    @staticmethod
    def init_app():
        """Create necessary directories if they don't exist"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TRAINED_MODELS_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.BASE_DIR, 'database'), exist_ok=True)
