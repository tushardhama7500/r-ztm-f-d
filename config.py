import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-should-be-in-.env')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a-very-jwt-secret-key')

    # Your custom DB settings
    MYSQL_DATABASE = 'task_manager_db'
    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = '*TU#sh2003'
    MYSQL_HOST = 'localhost'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)