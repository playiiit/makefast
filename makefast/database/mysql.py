import os
from dotenv import load_dotenv
from fastapi import FastAPI
import mysql.connector
from makefast.base_model.mysql import MySQLBase

load_dotenv()


class MySQLDatabaseInit:
    @staticmethod
    def init(app: FastAPI):
        @app.on_event("startup")
        async def startup_db_client():
            db_connection = MySQLDatabaseInit.get_database_connection()
            MySQLBase.set_database(db_connection)

        @app.on_event("shutdown")
        async def shutdown_db_client():
            MySQLBase.get_database().close()

    @staticmethod
    def get_database_connection():
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            port=os.getenv("DB_PORT")
        )
