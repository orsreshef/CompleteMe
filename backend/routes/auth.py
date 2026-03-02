"""
Authentication routes — register, login, logout, token refresh, current user.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from extensions import db, bcrypt, limiter
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ── Register ──────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    """Create a new user account."""
    data = request.get_json(silent=True) or {}

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    # Basic validation
    if not username or not email or not password:
        return jsonify({'error': 'Username, email and password are required.'}), 400

    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({'error': 'Invalid email address.'}), 400

    # Uniqueness check
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists.'}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'This username is already taken.'}), 409

    # Create user
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Issue tokens
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))

    response = jsonify({'message': 'Account created successfully.', 'user': user.to_dict()})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 201


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['POST'])
@limiter.limit('5 per 15 minutes')
def login():
    """Validate credentials and issue JWT cookies."""
    data = request.get_json(silent=True) or {}

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))

    response = jsonify({'message': 'Logged in successfully.', 'user': user.to_dict()})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear JWT cookies."""
    response = jsonify({'message': 'Logged out successfully.'})
    unset_jwt_cookies(response)
    return response, 200


# ── Refresh access token ──────────────────────────────────────────────────────

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token using the refresh cookie."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    response = jsonify({'message': 'Token refreshed.'})
    set_access_cookies(response, access_token)
    return response, 200


# ── Current user ──────────────────────────────────────────────────────────────

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Return the current authenticated user's profile."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found.'}), 404

    return jsonify({'user': user.to_dict()}), 200
