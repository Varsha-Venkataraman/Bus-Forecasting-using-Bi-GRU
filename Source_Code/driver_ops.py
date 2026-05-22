from db_utils import sql_connect, sql_disconnect

# ---------------- INSERT ----------------
def insert_driver(para):
    conn, cursor = sql_connect()
    if not conn: return
    sql = "INSERT INTO driver (name) VALUES (%s)"
    cursor.execute(sql, para)
    conn.commit()
    print("Driver inserted successfully.")
    sql_disconnect(conn, cursor)

# ---------------- DELETE ----------------
def delete_driver(driver_id):
    conn, cursor = sql_connect()
    if not conn:
        return
    try:
        cursor.execute("SELECT COUNT(*) AS bus_count FROM bus WHERE driver_id = %s", (driver_id,))
        row = cursor.fetchone()
        count = row["bus_count"] if row else 0
        if count > 0:
            raise Exception(f"Driver {driver_id} is assigned to {count} bus. Please reassign or delete the buses first.")

        cursor.execute("DELETE FROM driver WHERE id = %s", (driver_id,))
        conn.commit()
        print(f"Driver with ID {driver_id} deleted.")
    finally:
        sql_disconnect(conn, cursor)

# ---------------- UPDATE ----------------
def update_driver(para):
    conn, cursor = sql_connect()
    if not conn: return
    statement = '''
        UPDATE driver SET
            name = COALESCE(%s, name)
        WHERE id = %s;
    '''
    cursor.execute(statement, para)
    conn.commit()
    print(f"Driver with ID {para[-1]} updated.")
    sql_disconnect(conn, cursor)

# ---------------- SEARCH ----------------
def search(para):
    conn, cursor = sql_connect()
    if not conn: return
    try:
        driver_id, name = para

        statement = '''SELECT * FROM driver WHERE
            (%s IS NULL OR id = %s) AND
            (%s IS NULL OR name LIKE %s); '''
        params = [
            driver_id if driver_id else None, driver_id,
            name if name else None, f"%{name}%" if name else None
        ]

        cursor.execute(statement, params)
        print("Driver Search")
        rows = cursor.fetchall()
        return rows
    finally:
        sql_disconnect(conn, cursor)
