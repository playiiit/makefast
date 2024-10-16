import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class MySQLDatabase:
    def __init__(self):
        self.database_connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            port=os.getenv("DB_PORT")
        )

    def get_database(self):
        return self.database_connection


mysql_database = MySQLDatabase()
