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
    import os
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-this")
    from datetime import timedelta
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    jwt = JWTManager(app)
    
    # Connect to DB
    db.connect()
    
    # Global Error Handler
    from flask import jsonify
    from utils.logger import logger
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the internal error with traceback
        logger.exception(f"Unhandled Exception: {str(e)}")
        
        # Return standard JSON response
        response = {
            "error": "Internal Server Error",
            "message": str(e) if app.debug else "An unexpected error occurred"
        }
        return jsonify(response), 500

    @app.before_request
    def log_request_info():
        from flask import request
        logger.info(f"Request: {request.method} {request.full_path} from {request.remote_addr}")

    @app.after_request
    def log_response_info(response):
        from flask import request
        logger.info(f"Response: {request.method} {request.full_path} | Status: {response.status_code}")
        return response

    # Register Blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    from controllers.admin_controller import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from controllers.analytics_controller import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Swagger Documentation
    from flask import send_from_directory, render_template_string
    import os

    @app.route('/api/docs')
    def swagger_ui():
        return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>HealthAI API Docs</title>
                <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
                <style>
                    body { margin: 0; background: #fafafa; }
                </style>
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
                <script>
                    window.onload = () => {
                        window.ui = SwaggerUIBundle({
                            url: '/static/swagger.yaml',
                            dom_id: '#swagger-ui',
                            presets: [
                                SwaggerUIBundle.presets.apis,
                                SwaggerUIBundle.presets.all
                            ],
                            layout: "BaseLayout"
                        });
                    };
                </script>
            </body>
            </html>
        """)

    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
