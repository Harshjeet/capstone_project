from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import db
from controllers.api_controller import api

def create_app():
    app = Flask(__name__)
    # Allow specific origins for development
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]}}, supports_credentials=True)
    
    # JWT Config
    app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this"  # Change this!
    from datetime import timedelta
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    jwt = JWTManager(app)
    
    # Connect to DB
    db.connect()
    
    # Register Blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    from controllers.admin_controller import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from controllers.analytics_controller import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
