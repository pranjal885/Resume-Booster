import os
from flask import Flask, redirect, url_for, session
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
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
        try:
            db.create_all()
            print("[APP] All database tables checked/created successfully!")
        except Exception as e:
            print(f"[APP WARNING] Database connection during startup failed: {e}. Check MySQL configurations or wait for fallback.")
            
    return app

app = create_app()

if __name__ == '__main__':
    # Create upload directory if not exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Start Flask Development Server
    app.run(host='0.0.0.0', port=5000, debug=True)
