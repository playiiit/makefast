from dotenv import load_dotenv
from app.database.mysql import mysql_database

load_dotenv()


def mysql_connection_test():
    mysql_connection = mysql_database.get_database()
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT * FROM `users`") # Add your query here
    result = cursor.fetchall()
    for x in result:
        print(x)


if __name__ == "__main__":
    mysql_connection_test()
