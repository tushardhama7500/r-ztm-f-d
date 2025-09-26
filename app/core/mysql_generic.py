import pymysql as sql
import time
from app.core.logs import logw

class MySQL_connector():
    def __init__(self, address='', user='', password='', database=''):
        self.address = address
        self.user = user
        self.password = password
        self.database = database
        self.is_connected = 0
        self.max_retries = 5
        self.conn = None
        self.cur = None
        self._initialize_connection()

    def _initialize_connection(self):
        try:
            self.conn = sql.connect(host=self.address, user=self.user, password=self.password, database=self.database)
            self.cur = self.conn.cursor(sql.cursors.DictCursor)
            self.cur.execute('SELECT 1')
            self.is_connected = 1
            logw("info", "Database connection established.")
        except Exception as e:
            logw("error", f"Unable to establish connection: {e}")
            raise Exception(f'Unable to establish connection: {e}')

    def _reconnect(self):
        current_try = 0
        while current_try < self.max_retries:
            try:
                self._initialize_connection()
                if self.is_connected:
                    logw("info", "Successfully reconnected to the database.")
                    return
            except Exception as e:
                logw("error", f"Reconnection attempt failed ({current_try+1}/{self.max_retries}): {e}")
                current_try += 1
                time.sleep(1)
        raise Exception('Unable to reconnect after multiple attempts')


    def _execute_query(self, query, params=None):
        qtry = 0
        

        if self.conn is None or not self.conn.open:
            self._reconnect()
            
        self.cur = self.conn.cursor(sql.cursors.DictCursor)
        
        while qtry < self.max_retries:
            try:
                if params:
                    num_of_rows = self.cur.execute(query, params)
                else:
                    num_of_rows = self.cur.execute(query)
                
                return num_of_rows
            except (sql.err.OperationalError, sql.err.InternalError) as e:
                logw("error", f"Query failed. Attempting to reconnect. Error: {e}")
                qtry += 1
                self._reconnect()
                self.cur = self.conn.cursor(sql.cursors.DictCursor) 
            except Exception as e:
                logw("error", f"Unhandled query execution error: {e}")
                raise 
        logw("error", "Query retry limit exceeded.")
        raise Exception("Query retry limit exceeded.")

    def insert_query(self, query, params):
        logw("info", f"Executing INSERT query with parameters.")
        return self._execute_query(query, params)

    def select_query(self, query, params, flag='multi'):
        logw("info", f"Executing SELECT query with parameters.")
        self._execute_query(query, params)
        if flag and flag.lower() == 'multi':
            return self.cur.fetchall()
        elif flag and flag.lower() == 'single':
            return self.cur.fetchone()
        return None

    def update_query(self, query, params):
        logw("info", f"Executing UPDATE query with parameters.")
        return self._execute_query(query, params)

    def delete_query(self, query, params):
        logw("info", f"Executing DELETE query with parameters.")
        return self._execute_query(query, params)
    
    def close(self):
        try:
            if self.cur:
                self.cur.close()
                self.cur = None # Clear cursor reference
            
            if self.conn and self.conn.open:
                self.conn.close()
                self.conn = None # Clear connection reference
            logw("info", "Database connection closed successfully.")
        except Exception as e:
            logw("error", f"Error closing database connection: {e}")