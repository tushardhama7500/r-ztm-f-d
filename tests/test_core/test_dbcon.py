# tests/test_core/test_dbcon.py
import pytest
from unittest.mock import patch, MagicMock
from app.core.dbcon import get_db_connection, _db_connection

class TestDBConnection:
    def setup_method(self):
        global _db_connection
        _db_connection = None
    
    @patch('app.core.dbcon.MySQL_connector')
    @patch('app.core.dbcon.config_by_name')
    def test_get_db_connection_works(self, mock_config, mock_connector):
        mock_config_obj = MagicMock()
        mock_config_obj.MYSQL_HOST = 'localhost'
        mock_config_obj.MYSQL_USERNAME = 'test'
        mock_config_obj.MYSQL_PASSWORD = 'test'
        mock_config_obj.MYSQL_DATABASE = 'test_db'
        mock_config.__getitem__.return_value = mock_config_obj
        
        mock_instance = MagicMock()
        mock_instance.is_connected = 1
        mock_connector.return_value = mock_instance
        
        connection = get_db_connection()
        assert connection is mock_instance
    
    @patch('app.core.dbcon.MySQL_connector')
    @patch('app.core.dbcon.config_by_name')
    def test_get_db_connection_cached(self, mock_config, mock_connector):
        mock_config_obj = MagicMock()
        mock_config_obj.MYSQL_HOST = 'localhost'
        mock_config_obj.MYSQL_USERNAME = 'test'
        mock_config_obj.MYSQL_PASSWORD = 'test'
        mock_config_obj.MYSQL_DATABASE = 'test_db'
        mock_config.__getitem__.return_value = mock_config_obj
        
        mock_instance = MagicMock()
        mock_instance.is_connected = 1
        mock_connector.return_value = mock_instance
        
        connection1 = get_db_connection()
        connection2 = get_db_connection()
        assert connection1 is connection2