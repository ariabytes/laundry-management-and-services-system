from connection import get_db_connection

db = get_db_connection()
if db:
    print("Connected successfully!")
    cursor = db.cursor()
    cursor.execute("SHOW DATABASES;")
    for x in cursor:
        print(x)
    cursor.close()
    db.close()
else:
    print("Connection failed.")
