# Note: Since you're using raw SQL via your mysql_generic.py, 
# we'll define a class to represent the data, not as a SQLAlchemy model.

from app.core.dbcon import get_db_connection
from datetime import datetime

class Task:
    def __init__(self, id, title, description, completed, created_at, updated_at):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def get_all():
        db = get_db_connection()
        try:
            query = "SELECT * FROM tasks"
            # ✅ FIX 1: Pass empty tuple for required 'params' argument
            tasks_data = db.select_query(query, (), flag='multi') 
            return [Task(**task) for task in tasks_data] if tasks_data else []
        finally:
            db.close()
    
    @staticmethod
    def get_by_id(task_id):
        db = get_db_connection()
        try:
            # ✅ FIX 2: Use parameterized query to prevent SQL Injection
            query = "SELECT * FROM tasks WHERE id = %s"
            params = (task_id,)
            task_data = db.select_query(query, params, flag='single')
            return Task(**task_data) if task_data else None
        finally:
            db.close()

    def save(self):
        db = get_db_connection()
        try:
            if self.id: # Update existing task
                # ✅ FIX 3: Use parameterized query for UPDATE
                query = """
                    UPDATE tasks SET 
                    title=%s, description=%s, completed=%s, 
                    updated_at=%s WHERE id=%s
                """
                params = (
                    self.title, 
                    self.description, 
                    self.completed, 
                    datetime.now(), 
                    self.id
                )
                db.update_query(query, params)
            else: # Create new task
                # ✅ FIX 4: Use parameterized query for INSERT
                query = """
                    INSERT INTO tasks (title, description, completed, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                current_time = datetime.now()
                params = (
                    self.title, 
                    self.description, 
                    self.completed, 
                    current_time, 
                    current_time
                )
                self.id = db.insert_query(query, params)

            # ✅ FIX 5: Commit the transaction after write operations
            db.conn.commit()

        except Exception as e:
            # Rollback on error
            if db.conn and db.conn.open:
                db.conn.rollback()
            raise e
        finally:
            db.close()

    def delete(self):
        db = get_db_connection()
        try:
            # ✅ FIX 6: Use parameterized query for DELETE
            query = "DELETE FROM tasks WHERE id = %s"
            params = (self.id,)
            db.delete_query(query, params)
            
            # ✅ FIX 7: Commit the transaction
            db.conn.commit()
            
        except Exception as e:
            if db.conn and db.conn.open:
                db.conn.rollback()
            raise e
        finally:
            db.close()