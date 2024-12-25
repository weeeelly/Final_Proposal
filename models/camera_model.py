from utils.db_connection import DatabasePool

class CameraModel:
    @staticmethod
    def get_cameras(city, region):
        query = """
        SELECT 
            c.Limits, 
            c.Direction, 
            c.Address, 
            p.Deptnm, 
            p.Branchnm
        FROM 
            camera c
        INNER JOIN 
            Ps p ON c.Address = p.addr
        WHERE 
            p.City = %s AND p.Region = %s
        ORDER BY 
            c.Address
        """
        return DatabasePool.execute_query(query, (city, region))

    @staticmethod
    def update_camera(address, new_limit, user_id):
        # 檢查地址是否存在
        check_query = "SELECT Address FROM camera WHERE Address = %s"
        if not DatabasePool.execute_query(check_query, (address,)):
            raise ValueError("Camera address not found")

        # 更新速限
        update_query = """
        UPDATE camera 
        SET Limits = %s 
        WHERE Address = %s
        """
        DatabasePool.execute_update(update_query, (new_limit, address))

        # 記錄更新
        log_query = """
        INSERT INTO `update` (Uid, Addr) 
        VALUES (%s, %s)
        """
        return DatabasePool.execute_update(log_query, (user_id, address))

    @staticmethod
    def get_update_history(user_id):
        query = """
        SELECT 
            u.Addr,
            c.Limits,
            c.Direction,
            p.Deptnm,
            p.Branchnm
        FROM 
            `update` u
        JOIN 
            camera c ON u.Addr = c.Address
        JOIN 
            Ps p ON c.Address = p.addr
        WHERE 
            u.Uid = %s
        ORDER BY 
            u.Addr
        """
        return DatabasePool.execute_query(query, (user_id,))