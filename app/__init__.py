from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from config import config_by_name

# Corrected absolute import
from app.core.logs import logw

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize Swagger with basic template, security, definitions, and TAGS
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Task Manager API",
            "description": "API documentation for a simple task manager.",
            "version": "1.0.0"
        },
        # Explicitly define tags for grouping in the correct order
        "tags": [
            {
                "name": "tasks",
                "description": "Task management operations"
            },
            {
                "name": "authentication",
                "description": "User registration and login"
            }
        ],
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "definitions": {
            "Task": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "completed": {"type": "boolean"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                }
            }
        }
    })

    @app.errorhandler(404)
    def not_found(error):
        logw("error", f"404 Not Found: {error.description}")
        return jsonify({'message': 'Resource not found'}), 404

    # Register blueprints
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app