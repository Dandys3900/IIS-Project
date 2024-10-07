# Imports
import os
import pymysql

try:
    timeout = 10
    # Connect to database
    database = pymysql.connect(
        charset         = "utf8mb4",
        connect_timeout = timeout,
        read_timeout    = timeout,
        write_timeout   = timeout,
        cursorclass     = pymysql.cursors.DictCursor,
        port            = 17370,
        db              = "defaultdb",
        host            = "mysql-1eeb8483-iisproject2024.g.aivencloud.com",
        user            = "avnadmin",
        password        = "AVNS_nKlEyXmnpYpTucczgnZ"
    )
    print("Succesfully connected to database!")
except Exception as err:
    print(f"Error connecting to database: {err}")
