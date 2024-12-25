from utils.db_connection import DatabasePool

class UserModel:
    @staticmethod
    def validate_user(username, password):
        query = """
        SELECT Uid, Username 
        FROM User 
        WHERE Username = %s AND Password = %s
        """
        results = DatabasePool.execute_query(query, (username, password))
        return results[0] if results else None

    @staticmethod
    def register_user(username, password):
        # 先檢查用戶名是否存在
        check_query = "SELECT Uid FROM User WHERE Username = %s"
        existing_user = DatabasePool.execute_query(check_query, (username,))
        if existing_user:
            raise ValueError("Username already exists")

        query = """
        INSERT INTO User (Username, Password)
        VALUES (%s, %s)
        """
        return DatabasePool.execute_update(query, (username, password))