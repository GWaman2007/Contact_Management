from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with name, email, and password."""
    data = request.get_json(silent=True) or request.form.to_dict()

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({
            "status": 400,
            "error": "Bad Request",
            "message": "Name, email, and password are required."
        }), 400

    # Check if email is already registered
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "status": 409,
            "error": "Conflict",
            "message": "User with this email already exists."
        }), 409

    # Create new user and hash password
    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Generate JWT token
    token = create_access_token(identity=str(user.user_id))

    return jsonify({
        "status": 201,
        "message": "User registered successfully",
        "access_token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user with email and password."""
    data = request.get_json(silent=True) or request.form.to_dict()

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({
            "status": 400,
            "error": "Bad Request",
            "message": "Email and password are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({
            "status": 401,
            "error": "Unauthorized",
            "message": "Invalid email or password."
        }), 401

    token = create_access_token(identity=str(user.user_id))

    return jsonify({
        "status": 200,
        "message": "Login successful",
        "access_token": token,
        "user": user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get profile of current logged-in user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    if not user:
        return jsonify({
            "status": 404,
            "error": "Not Found",
            "message": "User not found."
        }), 404

    return jsonify({
        "status": 200,
        "user": user.to_dict()
    }), 200
