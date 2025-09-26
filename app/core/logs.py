import logging
import os
from datetime import date
from app.core.stamp import Stamp


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def file_creator(filename):
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(filename)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    return logger

log_file_mapping = {
    'info': os.path.join(LOGS_DIR, f"app_logs_{date.today()}.log"),
    'error': os.path.join(LOGS_DIR, f"error_logs_{date.today()}.log")
}

loggers = {log_type: file_creator(file_path) for log_type, file_path in log_file_mapping.items()}

def logw(logtype, message):

    if logtype not in loggers:
        return
    
    logger = loggers[logtype]
    unique_id = Stamp()
    log_message = f"{unique_id} {message}"
    
    if logtype == 'info':
        logger.info(log_message)
    elif logtype == 'error':
        logger.error(log_message, exc_info=True)
