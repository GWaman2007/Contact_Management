import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, send_from_directory, abort, render_template
from config import Config
from extensions import db, bcrypt, jwt
from routes.auth_routes import auth_bp
from routes.contact_routes import contact_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)

    # Ensure Upload Folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Frontend Page Routes
    @app.route('/', methods=['GET'])
    def home_page():
        return render_template('index.html')

    @app.route('/login', methods=['GET'])
    def login_page():
        return render_template('login_.html')

    @app.route('/register', methods=['GET'])
    def register_page():
        return render_template('Register.html')

    # Base Root Endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        return jsonify({
            "status": 200,
            "message": "Welcome to Contacts Store REST API",
            "endpoints": {
                "auth": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                    "me": "GET /api/auth/me"
                },
                "contacts": {
                    "create": "POST /create",
                    "get_all": "GET /get",
                    "get_one": "GET /get/<c_id>",
                    "search": "GET /search?q=<query>&code=<hide_code>",
                    "update": "PUT /update/<c_id>",
                    "delete": "DELETE /delete/<c_id>"
                }
            }
        }), 200

    # Route to trigger test 500 error for verification
    @app.route('/test-500', methods=['GET'])
    def trigger_500():
        abort(500)

    # ==================== ERROR HANDLERS ====================
    @app.errorhandler(404)
    def handle_404_error(error):
        """Custom REST 404 JSON Error Response."""
        return jsonify({
            "status": 404,
            "error": "Not Found",
            "message": "The requested endpoint or resource was not found on this server."
        }), 404

    @app.errorhandler(500)
    def handle_500_error(error):
        """Custom REST 500 JSON Error Response."""
        return jsonify({
            "status": 500,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server. Please try again later."
        }), 500

    @app.errorhandler(400)
    def handle_400_error(error):
        return jsonify({
            "status": 400,
            "error": "Bad Request",
            "message": str(error)
        }), 400

    @app.errorhandler(401)
    def handle_401_error(error):
        return jsonify({
            "status": 401,
            "error": "Unauthorized",
            "message": "Authentication token missing or invalid."
        }), 401

    # JWT Error handlers customization for clear REST responses
    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({
            "status": 401,
            "error": "Unauthorized",
            "message": "Authorization header missing or token not provided. Format: 'Authorization: Bearer <JWT_TOKEN>'"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            "status": 401,
            "error": "Unauthorized",
            "message": "Invalid JWT token signature or token formatted incorrectly."
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "status": 401,
            "error": "Unauthorized",
            "message": "JWT token has expired. Please log in again."
        }), 401

    # Create tables automatically inside application context
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
