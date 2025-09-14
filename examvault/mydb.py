import mysql.connector

dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='Shaiksha@7'
)

cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE papers")
print("completed!")
