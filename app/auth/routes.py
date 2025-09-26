from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flasgger import swag_from

from app.core.dbcon import get_db_connection
from app.core.logs import logw

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['authentication'],
    'summary': 'Register a new user',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': 'true',
            'schema': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'User registered successfully'},
        400: {'description': 'Username and password are required'},
        409: {'description': 'User already exists'}
    }
})
def register_user():
    """
    User Registration
    This endpoint allows a new user to register with a username and password.
    ---
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logw("error", "Registration failed: Missing username or password.")
        return jsonify({'message': 'Username and password are required'}), 400

    db = get_db_connection()
    try:
        user_exists = db.select_query("SELECT username FROM users WHERE username=%s", (username,), 'single')
        
        if user_exists: 
            logw("error", f"Registration failed: Username '{username}' already exists.")
            return jsonify({'message': 'User already exists'}), 409

        hashed_password = generate_password_hash(password)
        
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        params = (username, hashed_password)
        db.insert_query(query, params)
        
        db.conn.commit()
        
        logw("info", f"New user '{username}' registered successfully.")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        if hasattr(db, 'conn') and db.conn and db.conn.open:
            db.conn.rollback()
        
        logw("error", f"An unexpected error occurred during registration for user '{username}': {str(e)}")
        return jsonify({'message': f"Registration failed due to server error."}), 500
    finally:
        db.close()


@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['authentication'],
    'summary': 'User login',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': 'true',
            'schema': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Username and password are required'},
        401: {'description': 'Invalid credentials'}
    }
})
def login_user():
    """
    User Login
    This endpoint allows a user to log in and receive an access token.
    ---
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logw("error", "Login failed: Missing username or password.")
        return jsonify({'message': 'Username and password are required'}), 400

    db = get_db_connection()
    try:
        users = db.select_query("SELECT * FROM users WHERE username=%s", (username,), 'single')
        
        user = users 

        if user and check_password_hash(user['password'], password):
            access_token = create_access_token(identity=username)
            logw("info", f"User '{username}' logged in successfully.")
            return jsonify({'access_token': access_token}), 200

        logw("error", f"Login failed for user '{username}': Invalid credentials.")
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        logw("error", f"An error occurred during login for user '{username}': {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500
    finally:
        db.close()