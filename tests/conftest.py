# tests/conftest.py
import pytest
import os
import sys
from datetime import datetime

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import config_by_name

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('dev')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use in-memory database or test database
    app.config['MYSQL_DATABASE'] = 'test_task_manager_db'
    
    yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Register a test user
    client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Login and get token
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}