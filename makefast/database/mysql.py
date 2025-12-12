import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI
from mysql.connector import pooling, Error
from makefast.base_model.mysql import MySQLBase

load_dotenv()


class MySQLDatabaseInit:
    pool = None

    @staticmethod
    def init(app: FastAPI):
        @app.on_event("startup")
        async def startup_db_client():
            print("🔄 Initializing MySQL pool...")
            MySQLDatabaseInit.wait_for_database()
            MySQLBase.set_database(MySQLDatabaseInit.pool)
            print("✅ MySQL pool initialized.")

        @app.on_event("shutdown")
        async def shutdown_db_client():
            print("🛑 Closing MySQL pool...")
            # Pool connections auto-close on container stop
            pass

    # ============================
    # Create MySQL connection pool
    # ============================
    @staticmethod
    def create_pool():
        return pooling.MySQLConnectionPool(
            pool_name="main_pool",
            pool_size=10,
            pool_reset_session=True,
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            port=int(os.getenv("DB_PORT", 3306)),
            connect_timeout=30,
            autocommit=True,
            pool_overflow=5,
        )

    # =================================================
    # Retry until MySQL is ready (fixes startup crashes)
    # =================================================
    @staticmethod
    def wait_for_database(retries=15, delay=3):
        for attempt in range(1, retries + 1):
            try:
                print(f"⏳ Connecting to MySQL... attempt {attempt}/{retries}")
                MySQLDatabaseInit.pool = MySQLDatabaseInit.create_pool()

                # Test one connection
                conn = MySQLDatabaseInit.pool.get_connection()
                conn.close()

                print("✔ MySQL is reachable.")
                return
            except Error as e:
                print(f"🚫 MySQL not ready: {str(e)}")
                time.sleep(delay)

        raise Exception("❌ MySQL not available after multiple retries.")

    # =============================
    # For MakeFast's MySQLBase usage
    # =============================
    @staticmethod
    def get_connection():
        if MySQLDatabaseInit.pool is None:
            raise Exception("❌ MySQL pool is not initialized.")
        return MySQLDatabaseInit.pool.get_connection()
