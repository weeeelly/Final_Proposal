from mysql.connector import pooling
from config.database_config import DB_CONFIG

class DatabasePool:
    _instance = None
    _pool = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._pool = pooling.MySQLConnectionPool(**DB_CONFIG)
        return cls._instance

    def get_connection(self):
        return self._pool.get_connection()

    @staticmethod
    def execute_query(query, params=None, dictionary=True):
        conn = None
        cursor = None
        try:
            conn = DatabasePool.get_instance().get_connection()
            cursor = conn.cursor(dictionary=dictionary)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def execute_update(query, params=None):
        conn = None
        cursor = None
        try:
            conn = DatabasePool.get_instance().get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()