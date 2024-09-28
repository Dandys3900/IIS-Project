# Imports
import os
import pymysql

# Function for executing given SQL script
def executeSQLscript(cursor, filepath):
    # Try to open script file
    with open(filepath, 'r') as file:
        script = file.read()

    # Strip script into individual statements
    # NOTE: Script commands must be delimited by ';'
    statements = script.split(';')
    # Remove whitespaces from commands
    statements = [command.strip() for command in statements]

    # Execute it
    for command in statements:
        try:
            cursor.execute(command)
        except Exception as err:
            print(f"Error executing command: {command}; error: {err}")
            return

try:
    timeout = 10
    # Connect to database
    database = pymysql.connect(
        charset         = "utf8mb4",
        connect_timeout = 10,
        cursorclass     = pymysql.cursors.DictCursor,
        read_timeout    = timeout,
        port            = 17370,
        write_timeout   = timeout,
        db              = "defaultdb",
        host            = "mysql-1eeb8483-iisproject2024.g.aivencloud.com",
        user            = "avnadmin",
        password        = "AVNS_nKlEyXmnpYpTucczgnZ"
    )
    print("Succesfully connected to database!")
except Exception as err:
    print(f"Error connecting to database: {err}")
else:
    # Create cursor object
    cursor = database.cursor()
    # Execute script to create database
    executeSQLscript(cursor, os.path.join("source", "dbinit.sql"))
