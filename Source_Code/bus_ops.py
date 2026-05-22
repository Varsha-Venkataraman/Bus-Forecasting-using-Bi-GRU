from db_utils import sql_connect, sql_disconnect

#------- INSERT -------
def insert_bus(para):
    conn, cursor = sql_connect()
    if not conn: return
    sql = """
    INSERT INTO bus (route, bus_no, license_no, expiry, capacity, driver_id)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, para)
    conn.commit()
    print("Bus inserted successfully.")
    sql_disconnect(conn, cursor)

#------- DELETE -------
def delete_bus(bus_id):
    conn, cursor = sql_connect()
    if not conn: return
    sql = "DELETE FROM bus WHERE id = %s"
    cursor.execute(sql, (bus_id,))
    conn.commit()
    print(f"Bus with ID {bus_id} deleted.")
    sql_disconnect(conn, cursor)

#------- UPDATE -------
def update_bus(para):
    conn, cursor = sql_connect()
    if not conn: return
    statement = '''
        UPDATE bus SET
            route = COALESCE(%s, route),
            bus_no = COALESCE(%s, bus_no),
            license_no = COALESCE(%s, license_no),
            expiry = COALESCE(%s, expiry),
            capacity = COALESCE(%s, capacity),
            driver_id = COALESCE(%s, driver_id)
        WHERE id = %s;
    '''
    cursor.execute(statement, para)
    conn.commit()
    print(f"Bus with ID {para[-1]} updated.")
    sql_disconnect(conn, cursor)

#------- SEARCH -------
def search_bus(para):
    conn, cursor = sql_connect()
    if not conn: return
    try:
        bus_id, route, bus_no, license_no, expiry, capacity, driver_id = para

        statement = '''
            SELECT * FROM bus WHERE
            (%s IS NULL OR id = %s) AND
            (%s IS NULL OR route LIKE %s) AND
            (%s IS NULL OR bus_no = %s) AND
            (%s IS NULL OR license_no LIKE %s) AND
            (%s IS NULL OR DATE(expiry) = %s) AND
            (%s IS NULL OR capacity = %s) AND
            (%s IS NULL OR driver_id = %s);
        '''

        params = [
            bus_id if bus_id else None, bus_id,
            route if route else None, f"%{route}%" if route else None,   # substring
            bus_no if bus_no else None, bus_no,
            license_no if license_no else None, f"%{license_no}%" if license_no else None,  # substring
            expiry if expiry else None, expiry,
            capacity if capacity else None, capacity,
            driver_id if driver_id else None, driver_id   # exact match
        ]

        cursor.execute(statement, params)
        print("Bus Search")
        rows = cursor.fetchall()
        return rows
    finally:
        sql_disconnect(conn, cursor)
