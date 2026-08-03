from abc import ABC, abstractmethod
from typing import List, Optional

class Task(dict):
    """task model: id, title, done."""
    pass

class TaskRepository(ABC):

    """abstract task storage interface"""

    @abstractmethod
    def get_all(self) -> List[Task]:
        """return all tasks"""
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """return task or none."""
        pass

    @abstractmethod
    def create(self, title: str) -> Task:
        """insert task, return created task with id"""
        pass

    @abstractmethod
    def update(self, task_id: int, title: str) -> Optional[Task]:
        """update task, return updated task or none if not found"""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """delete task, return true if found, false otherwise"""
        pass

class PostgresRepository(TaskRepository):
    """tasks stored in postgres (docker)"""

    def __init__(self, connection_string: str):
        """connection_string: 'postgresql://user:pass@host:port/dbname'"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        self.psycopg2 = psycopg2
        self.RealDictCursor = RealDictCursor
        self.conn_string = connection_string

    def _get_conn(self):
        """open a connection to postgres"""
        return self.psycopg2.connect(self.conn_string)

    def _init_db(self):
        """create table if missing, seed if empty"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)

        # check if seeded
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        # seed if empty
        if count == 0:
            cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Buy milk", False))
            cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Write README", False))
            cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("walk dog", True))

        conn.commit()
        conn.close()

    def get_all(self) -> List[Task]:
        self._ensure_db()
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=self.RealDictCursor)
        cursor.execute("SELECT id, title, done FROM tasks ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        return [Task(**row) for row in rows]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        self._ensure_db()
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=self.RealDictCursor)
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
        row = cursor.fetchone()
        conn.close()
        return Task(**row) if row else None

    def create(self, title: str) -> Task:
        self._ensure_db()
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id", (title, False))
        new_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return Task(id=new_id, title=title, done=False)

    def update(self, task_id: int, title: str) -> Optional[Task]:
        self._ensure_db()
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET title = %s WHERE id = %s", (title, task_id))
        conn.commit()
        found = cursor.rowcount > 0
        conn.close()
        return Task(id=task_id, title=title, done=False) if found else None

    def delete(self, task_id: int) -> bool:
        self._ensure_db()
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        found = cursor.rowcount > 0
        conn.close()
        return found

    def _ensure_db(self): 
        """create table on first use, not on init"""
        if not hasattr(self, '_db_initialized'):
            self._init_db()
            self._db_initialized = True