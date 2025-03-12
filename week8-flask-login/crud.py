import sqlite3

conn = sqlite3.connect("inventory.db")

cursor = conn.cursor()

# create schema
with open("schema.sql", "r") as schema:
    cursor.executescript(schema.read())
# insert data
with open("data.sql", "r") as data:
    cursor.executescript(data.read())

cursor.execute("DELETE FROM ingredient WHERE ingredient_name IS NULL")
cursor.execute("UPDATE ingredient SET ingredient_name = 'jiaozi dumplings' WHERE ingredient_name ='jiaozi'")


conn.commit()
conn.close()