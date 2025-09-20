import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # leave this blank if your phpMyAdmin says 'No'
        database="laundry_db"
    )
    print("Connected successfully!")
except mysql.connector.Error as err:
    print(f"Connection failed: {err}")
