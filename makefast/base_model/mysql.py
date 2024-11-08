from typing import List, Dict, Any
from fastapi import HTTPException
from mysql.connector import Error


class MySQLBase:
    table_name: str = ""
    columns: List[str] = []
    _database = None

    @classmethod
    def set_database(cls, database):
        cls._database = database

    @classmethod
    def get_database(cls):
        return cls._database

    @classmethod
    def get_connection(cls):
        try:
            return cls.get_database()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error accessing mysql database: {str(e)}")

    @classmethod
    async def create(cls, **kwargs) -> Dict[str, Any]:
        connection = cls.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['%s'] * len(kwargs))
            query = f"INSERT INTO {cls.table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(kwargs.values()))
            connection.commit()
            return {**kwargs, "id": cursor.lastrowid}
        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()

    @classmethod
    async def find(cls, id: int) -> Dict[str, Any]:
        connection = cls.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            query = f"SELECT * FROM {cls.table_name} WHERE id = %s"
            cursor.execute(query, (id,))
            result = cursor.fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return result
        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()

    @classmethod
    async def all(cls) -> List[Dict[str, Any]]:
        connection = cls.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            query = f"SELECT * FROM {cls.table_name}"
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()

    @classmethod
    async def update(cls, id: int, **kwargs) -> Dict[str, Any]:
        connection = cls.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
            query = f"UPDATE {cls.table_name} SET {set_clause} WHERE id = %s"
            cursor.execute(query, list(kwargs.values()) + [id])
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item not found")
            return await cls.find(id)
        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()

    @classmethod
    async def delete(cls, id: int) -> Dict[str, bool]:
        connection = cls.get_connection()
        cursor = connection.cursor()
        try:
            query = f"DELETE FROM {cls.table_name} WHERE id = %s"
            cursor.execute(query, (id,))
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item not found")
            return {"success": True}
        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
