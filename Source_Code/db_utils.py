import mysql.connector
def sql_connect():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="<username>",
            password="<password>",
            database="vehicle_mgt"
        )
        cursor = conn.cursor(dictionary=True)
        print("SQL Connected")
        return conn, cursor
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None, None

def sql_disconnect(conn, cursor):
    if cursor:
        cursor.close()
    if conn and conn.is_connected():
        conn.close()
        print("SQL Disconnected\n\n")
