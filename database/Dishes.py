import pymysql
from database.DataBase import DatabaseConnection


class Dishes:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.conn = self.db_connection.connect()
        self.cursor = None
        if self.conn:
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def get_dish_by_id(self, dish_id):
        if self.cursor:
            query = "SELECT * FROM dish WHERE id = %s"
            try:
                self.cursor.execute(query, (dish_id,))
                result = self.cursor.fetchone()
                return result
            except pymysql.Error as e:
                print(f"查询菜品失败: {e}")
        return None

    def get_all_dishes(self):
        if self.cursor:
            query = "SELECT * FROM dish"
            try:
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                return results
            except pymysql.Error as e:
                print(f"查询所有菜品失败: {e}")
        return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()