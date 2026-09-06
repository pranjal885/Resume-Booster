import os
#os is Python's built-in module for interacting with the operating system.
from dotenv import load_dotenv
#This comes from the python-dotenv package.Its job is to read your:.env file.


# Load environment variables from .env file
load_dotenv()

class Config:
#You're creating a class whose purpose is to store application configuration.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_resume_booster_2026')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    #__file__ means:The path of the current Python file (config.py).
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    #Flask can use this configuration to limit the size of incoming requests/uploads.
    #For your project, this prevents someone from uploading an unnecessarily huge file.
    ALLOWED_EXTENSIONS = {'pdf'}

    @staticmethod
    def get_db_uri():
    #This function determines: Which database should Resume Booster use?
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
            #PyMySQL is the Python driver used to communicate with MySQL.

            # Connect without DB first to ensure we can create it if not exists
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                port=int(db_port), #Why int()? Because environment variables are read as strings.
                connect_timeout=2 #Don't wait forever for MySQL. Give the connection attempt about 2 seconds.
                #That's why your application can quickly fall back to SQLite if MySQL isn't responding.
            )
            with conn.cursor() as cursor:
                #A cursor is used to execute SQL statements against the database connection.
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            conn.commit()
            conn.close()
            print(f"[DB INFO] Successfully connected to MySQL at {db_host} and ensured database '{db_name}' exists.")
            return mysql_uri #tells SQLAlchemy:"Use MySQL."
        except Exception as e:
            sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resume_booster.db')
            print(f"[DB WARNING] Failed to connect to MySQL ({e}). Falling back to SQLite: {sqlite_path}")
            return f"sqlite:///{sqlite_path}"

    SQLALCHEMY_DATABASE_URI = get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False #This tells Flask-SQLAlchemy not to track every modification made to objects.
