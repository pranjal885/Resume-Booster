import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_resume_booster_2026')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf'}

    @staticmethod
    def get_db_uri():
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD', '')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '3306')
        db_name = os.environ.get('DB_NAME', 'resume_booster')
        
        # If no user is specified, fall back to SQLite
        if not db_user:
            sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resume_booster.db')
            print(f"[DB INFO] No DB_USER environment variable set. Using SQLite: {sqlite_path}")
            return f"sqlite:///{sqlite_path}"
            
        mysql_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Test connecting using pymysql
        try:
            import pymysql
            # Connect without DB first to ensure we can create it if not exists
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                port=int(db_port),
                connect_timeout=2
            )
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            conn.commit()
            conn.close()
            print(f"[DB INFO] Successfully connected to MySQL at {db_host} and ensured database '{db_name}' exists.")
            return mysql_uri
        except Exception as e:
            sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resume_booster.db')
            print(f"[DB WARNING] Failed to connect to MySQL ({e}). Falling back to SQLite: {sqlite_path}")
            return f"sqlite:///{sqlite_path}"

    SQLALCHEMY_DATABASE_URI = get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
