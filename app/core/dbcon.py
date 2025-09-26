from app.core.mysql_generic import MySQL_connector
from config import config_by_name
from app.core.logs import logw

_db_connection = None

def get_db_connection():
    global _db_connection
    if _db_connection is None or not _db_connection.is_connected:
        try:
            cfg = config_by_name['dev']
            _db_connection = MySQL_connector(
                address=cfg.MYSQL_HOST,
                user=cfg.MYSQL_USERNAME,
                password=cfg.MYSQL_PASSWORD,
                database=cfg.MYSQL_DATABASE
            )
        except Exception as e:
            logw("error", f"Failed to get database connection: {e}")
            return None
    return _db_connection