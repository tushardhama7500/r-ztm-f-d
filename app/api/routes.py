from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from datetime import datetime 


from app.models import Task
from app.core.logs import logw

api_bp = Blueprint('api', __name__, url_prefix='/api/v1') 

def task_to_dict(task, created_by=None):
    """Helper function to convert Task object to a clean dictionary for JSON response."""
    if not task:
        return None
    
    task_dict = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': bool(task.completed), 
        'created_at': str(task.created_at),
        'updated_at': str(task.updated_at),
        'created_by': created_by if created_by else "unknown_user" 
    }
    return task_dict

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['tasks'],
    'security': [{'BearerAuth': []}],
    'summary': 'Retrieve a list of all tasks',
    'responses': {
        200: {
            'description': 'A list of tasks',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Task'}
            }
        },
        500: {'description': 'Server error'}
    }
})
def get_tasks():
    """
    Get all tasks
    This endpoint retrieves all tasks from the database.
    ---
    """
    current_user_identity = get_jwt_identity()
    logw("info", f"User {current_user_identity} is retrieving all tasks.")
    try:
        tasks = Task.get_all()
        tasks_list = [task_to_dict(t, current_user_identity) for t in tasks]
        return jsonify(tasks_list), 200
    except Exception as e:
        logw("error", f"Error retrieving tasks for user {current_user_identity}: {str(e)}")
        return jsonify({'message': 'Failed to retrieve tasks'}), 500


@api_bp.route('/tasks/<int:id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['tasks'],
    'security': [{'BearerAuth': []}],
    'summary': 'Retrieve a specific task',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': 'true',
            'description': 'The ID of the task to retrieve.'
        }
    ],
    'responses': {
        200: {'description': 'Task details','schema': {'$ref': '#/definitions/Task'}},
        404: {'description': 'Task not found'},
        500: {'description': 'Server error'}
    }
})
def get_task(id):
    """
    Get a specific task
    This endpoint retrieves the details of a single task by its ID.
    ---
    """
    current_user_identity = get_jwt_identity()
    logw("info", f"User {current_user_identity} is retrieving task with ID {id}.")
    try:
        task = Task.get_by_id(id)
        if task:
            return jsonify(task_to_dict(task, current_user_identity)), 200
        
        logw("error", f"Task with ID {id} not found for user {current_user_identity}.")
        return jsonify({'message': 'Task not found'}), 404
    except Exception as e:
        logw("error", f"Error retrieving task {id}: {str(e)}")
        return jsonify({'message': 'Failed to retrieve task'}), 500


@api_bp.route('/tasks', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['tasks'],
    'security': [{'BearerAuth': []}],
    'summary': 'Create a new task',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': 'true',
            'schema': {
                'type': 'object',
                'required': ['title'],
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Task created successfully', 'schema': {'$ref': '#/definitions/Task'}},
        400: {'description': 'Title is required'}
    }
})
def create_task():
    """
    Create a task
    This endpoint creates a new task.
    ---
    """
    data = request.get_json()
    current_user_identity = get_jwt_identity()
    
    if not data or 'title' not in data:
        logw("error", f"User {current_user_identity} failed to create task: Missing 'title'.")
        return jsonify({'message': 'Title is required'}), 400

    try:
        new_task = Task(
            id=None, 
            title=data['title'], 
            description=data.get('description', ''), 
            completed=False, 
            created_at=datetime.now(),
            updated_at=datetime.now()
            # NOTE: If you add 'user_id' to your Task constructor/DB, you must pass it here.
        )
        new_task.save()
        
        logw("info", f"User {current_user_identity} created new task with ID {new_task.id}.")
        return jsonify(task_to_dict(new_task, current_user_identity)), 201
    except Exception as e:
        logw("error", f"Error creating task for user {current_user_identity}: {str(e)}")
        return jsonify({'message': 'Failed to create task'}), 500


@api_bp.route('/tasks/<int:id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['tasks'],
    'security': [{'BearerAuth': []}],
    'summary': 'Update a task',
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': 'true', 'description': 'The ID of the task to update.'},
        {'name': 'body', 'in': 'body', 'required': 'true', 'schema': {'type': 'object', 'properties': {'title': {'type': 'string'}, 'description': {'type': 'string'}, 'completed': {'type': 'boolean'}}}}
    ],
    'responses': {
        200: {'description': 'Task updated successfully', 'schema': {'$ref': '#/definitions/Task'}},
        404: {'description': 'Task not found'}
    }
})
def update_task(id):
    """
    Update a task
    This endpoint updates the details of an existing task.
    ---
    """
    data = request.get_json()
    current_user_identity = get_jwt_identity()
    
    try:
        task = Task.get_by_id(id)
        if not task:
            logw("error", f"User {current_user_identity} failed to update task with ID {id}: Task not found.")
            return jsonify({'message': 'Task not found'}), 404

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)
        task.updated_at = datetime.now() 
        
        task.save()
        
        logw("info", f"User {current_user_identity} updated task with ID {id}.")
        return jsonify(task_to_dict(task, current_user_identity)), 200
    except Exception as e:
        logw("error", f"Error updating task {id}: {str(e)}")
        return jsonify({'message': 'Failed to update task'}), 500


@api_bp.route('/tasks/<int:id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['tasks'],
    'security': [{'BearerAuth': []}],
    'summary': 'Delete a task',
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': 'true', 'description': 'The ID of the task to delete.'}
    ],
    'responses': {
        200: {'description': 'Task deleted successfully'},
        404: {'description': 'Task not found'}
    }
})
def delete_task(id):
    """
    Delete a task
    This endpoint deletes a task by its ID.
    ---
    """
    current_user_identity = get_jwt_identity()
    try:
        task = Task.get_by_id(id)
        if not task:
            logw("error", f"User {current_user_identity} failed to delete task with ID {id}: Task not found.")
            return jsonify({'message': 'Task not found'}), 404

        task.delete()
        logw("info", f"User {current_user_identity} deleted task with ID {id}.")
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        logw("error", f"Error deleting task {id}: {str(e)}")
        return jsonify({'message': 'Failed to delete task'}), 500