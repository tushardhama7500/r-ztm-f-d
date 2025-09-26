# tests/test_core/test_logs.py
import pytest
import os
import tempfile
import logging
from datetime import date
from app.core.logs import file_creator, logw, log_file_mapping, loggers

@pytest.fixture
def setup_logs():
    """Setup temporary files for testing"""
    temp_dir = tempfile.mkdtemp()
    original_mapping = log_file_mapping.copy()
    
    # Use temporary files for testing
    log_file_mapping['info'] = os.path.join(temp_dir, f"test_info_{date.today()}.log")
    log_file_mapping['error'] = os.path.join(temp_dir, f"test_error_{date.today()}.log")
    
    # Clear existing loggers and handlers to avoid conflicts
    for logger in loggers.values():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    # Recreate loggers with new file paths
    loggers.clear()
    loggers.update({log_type: file_creator(file_path) for log_type, file_path in log_file_mapping.items()})
    
    yield temp_dir, original_mapping
    
    # Teardown
    for logger in loggers.values():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    log_file_mapping.update(original_mapping)
    loggers.clear()
    loggers.update({log_type: file_creator(file_path) for log_type, file_path in log_file_mapping.items()})
    
    import shutil
    shutil.rmtree(temp_dir)

def test_file_creator_creates_logger(setup_logs):
    """Test that file_creator returns a logger"""
    temp_dir, _ = setup_logs
    temp_file = os.path.join(temp_dir, "test.log")
    logger = file_creator(temp_file)
    assert isinstance(logger, logging.Logger)
    
    # Clean up
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

def test_file_creator_same_file_returns_same_logger(setup_logs):
    """Test that file_creator returns same logger for same file"""
    temp_dir, _ = setup_logs
    temp_file = os.path.join(temp_dir, "test.log")
    logger1 = file_creator(temp_file)
    logger2 = file_creator(temp_file)
    assert logger1 is logger2
    
    # Clean up
    for handler in logger1.handlers[:]:
        handler.close()
        logger1.removeHandler(handler)

def test_logw_info_message(setup_logs):
    """Test logging info messages"""
    temp_dir, _ = setup_logs
    logw('info', 'Test info message')
    
    # Force flush the logs
    loggers['info'].handlers[0].flush()
    
    # Check if file was created and contains message
    assert os.path.exists(log_file_mapping['info'])
    with open(log_file_mapping['info'], 'r') as f:
        content = f.read()
        assert 'Test info message' in content

def test_logw_error_message(setup_logs):
    """Test logging error messages"""
    temp_dir, _ = setup_logs
    try:
        raise ValueError("Test error")
    except ValueError:
        logw('error', 'Test error message')
    
    # Force flush the logs
    loggers['error'].handlers[0].flush()
    
    # Check if file was created and contains message
    assert os.path.exists(log_file_mapping['error'])
    with open(log_file_mapping['error'], 'r') as f:
        content = f.read()
        assert 'Test error message' in content

def test_logw_invalid_logtype(setup_logs):
    """Test logging with invalid log type"""
    temp_dir, _ = setup_logs
    # Should not raise an exception
    logw('invalid', 'This should not be logged')

def test_logw_message_format(setup_logs):
    """Test that log messages contain stamp"""
    temp_dir, _ = setup_logs
    test_message = "Test format message"
    logw('info', test_message)
    
    # Force flush the logs
    loggers['info'].handlers[0].flush()
    
    with open(log_file_mapping['info'], 'r') as f:
        content = f.read().strip()
        # Should contain timestamp and message
        assert '[' in content and ']' in content
        assert test_message in content