import os
import sys

# Add the parent directory to the path so we can import config and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config
from models import db

def init_database():
    """
    Initializes database tables based on Config URI.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    print("[DB] Initializing database connection...")
    
    with app.app_context():
        try:
            print("[DB] Drop/create tables checking...")
            # Create all tables defined in models package
            db.create_all()
            print("[DB] All database tables created successfully!")
        except Exception as e:
            print(f"[DB ERROR] Failed to create database tables: {e}")
            sys.exit(1)

if __name__ == '__main__':
    init_database()
