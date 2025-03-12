from flask import Flask, g
from flask_bcrypt import Bcrypt

import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

DATABASE = 'inventory.db'

# connect database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

#initialize db
def init_db():
    with app.app_context():
        db = get_db()
        cur = db.cursor()

    try:
        print("Initializing database...")  # Debug message

        # Run schema.sql
        with app.open_resource('schema.sql', 'r') as schema:
            schema_sql = schema.read()
            print("Executing schema.sql...")
            cur.executescript(schema_sql)

        # Run data.sql
        with open("data.sql", "r") as data:
            data_sql = data.read()
            print("Executing data.sql...")
            cur.executescript(data_sql)

        db.commit()
        print("Database initialized successfully.")

        # insert initial user with hashed password
        username = "ella"
        email = "ella@ella.com"
        plaintext_password = "P@ssw0rd!example"

        hashed_password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

        cur.execute("""
            INSERT INTO user (username, email, hashed_password) 
            VALUES (?, ?, ?)
        """, (username, email, hashed_password))

        db.commit()
        print(f"Inserted initial user: {username}")

    except Exception as e:
        print(f"Error initializing database: {e}")

init_db()