import pymysql


class DatabaseConfig:
    def __init__(self):
        pass

    def get_config(self):
        host = '127.0.0.1'
        port = 3306
        user = 'root'
        password = '123456'
        database = 'smart_restaurant'
        return host, port, user, password, database



class DatabaseConnection:
    def __init__(self):
        self.config = DatabaseConfig()
        self.conn = None

    def connect(self):
        db_config = self.config.get_config()
        if db_config:
            try:
                host, port, user, password, database = db_config
                self.conn = pymysql.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port
                )
                return self.conn
            except pymysql.Error as e:
                print(f"错误,数据库连接失败: {e}")
                return None
        return None