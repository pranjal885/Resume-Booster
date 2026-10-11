import os  #Python's way of interacting with files, folders, paths, environment variables, etc.
from flask import Flask, redirect, url_for, session
#url_for : Flask can generate the URL from the route's name.
#session : This stores information about the current logged-in user.
from config import Config
#this contains the configuration settings for the Flask application, such as database connection details, secret keys, and other environment-specific settings.
from models import db
#Your models package contains the SQLAlchemy database object.
#db represents the connection/interface between Flask and your database.


def create_app():
#this is called an application factory. It creates and configures the Flask application.
    app = Flask(__name__)  #__name__ is a special Python variable.
    #Flask(__name__) creates the Flask application.
    app.config.from_object(Config)
    #This takes the settings from your Config class and puts them into the Flask application's configuration.

    # Initialize DB
    db.init_app(app) #Connects Flask app with SQLAlchemy database.
    
    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.analyze import analyze_bp
    from routes.chat import chat_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(chat_bp)
    
    # Global context processor to make session variables available in templates
    @app.context_processor
    def inject_user():
        return dict(current_user_name=session.get('username'))

    # Custom template filter to load JSON strings inside templates
    @app.template_filter('json_loads')
    def json_loads_filter(s):
    #You want to turn json strings into an actual Python object.
        import json
        if not s:
            return {}
        try:
            return json.loads(s)
        except Exception:
            return {}

        
    # Redirect root to dashboard (which handles auth redirect)
    @app.route('/')
    def root():
        return redirect(url_for('dashboard.index'))
        
    # Ensure database tables exist at start
    with app.app_context():
    #Flask has something called an application context.
    #For the code inside this block, consider this Flask application to be the active application.
        try:
            db.create_all()
            #checks the SQLAlchemy models and creates the database tables if they don't already exist.
            print("[APP] All database tables checked/created successfully!")
        except Exception as e:
            print(f"[APP WARNING] Database connection during startup failed: {e}. Check MySQL configurations or wait for fallback.")
            
    return app

app = create_app()

if __name__ == '__main__':
#Run the following code only when this file is being executed directly.So if you do: python app.py this condition is true.
#But if another Python file imports: from app import app
#the code inside this block doesn't execute.

    # Create upload directory if not exists
    #exist_ok=True,,means:"If the folder already exists, don't throw an error."
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Start Flask Development Server
    app.run(host='0.0.0.0', port=5000, debug=True)
    #host='0.0.0.0'..Means Flask listens on all network interfaces.
    #debug=True...Enables Flask's development/debug mode.
    #It helps during development because changes can trigger automatic reloads and errors provide debugging information.