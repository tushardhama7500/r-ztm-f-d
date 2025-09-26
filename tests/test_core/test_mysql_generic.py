# tests/test_core/test_mysql_generic.py
import pytest
import pymysql
from unittest.mock import patch, MagicMock
from app.core.mysql_generic import MySQL_connector

class TestMySQLConnector:
    def test_initialization_success(self):
        """Test successful database connection initialization"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.return_value = None
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            assert connector.is_connected == 1
            mock_connect.assert_called_once()

    def test_initialization_failure(self):
        """Test database connection failure"""
        with patch('pymysql.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception, match="Unable to establish connection"):
                MySQL_connector(
                    address='localhost',
                    user='test',
                    password='test',
                    database='test_db'
                )

    def test_execute_query_success(self):
        """Test successful query execution"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.return_value = 1
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            result = connector._execute_query("SELECT 1")
            assert result == 1

    def test_execute_query_with_params(self):
        """Test query execution with parameters"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.return_value = 1
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            result = connector._execute_query("SELECT * FROM table WHERE id = %s", (1,))
            assert result == 1

    def test_reconnect_success(self):
        """Test successful reconnection"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.return_value = None
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            connector.is_connected = 0
            mock_conn.open = False
            
            with patch('time.sleep'):
                connector._reconnect()
            
            assert connector.is_connected == 1

    def test_reconnect_after_disconnection(self):
        """Test reconnection when connection is lost"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.return_value = 1
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            connector.is_connected = 0
            mock_conn.open = False
            
            with patch('time.sleep'):
                result = connector._execute_query("SELECT 1")
            assert result == 1

    def test_close_connection(self):
        """Test closing database connection"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            connector.close()
            
            mock_cursor.close.assert_called_once()
            mock_conn.close.assert_called_once()

    def test_select_query_multi(self):
        """Test SELECT query with multi-row result"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.return_value = 2
            mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            result = connector.select_query("SELECT * FROM table", None, 'multi')
            assert result == [{'id': 1}, {'id': 2}]

    def test_select_query_single(self):
        """Test SELECT query with single-row result"""
        with patch('pymysql.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.return_value = 1
            mock_cursor.fetchone.return_value = {'id': 1}
            mock_conn.open = True
            
            connector = MySQL_connector(
                address='localhost',
                user='test',
                password='test',
                database='test_db'
            )
            
            result = connector.select_query("SELECT * FROM table WHERE id = 1", None, 'single')
            assert result == {'id': 1}