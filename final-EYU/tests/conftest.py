import sys
import os
import pytest
import sqlite3
from flaskapp import app as flask_app, get_db

@pytest.fixture(scope="function")
def app():

    test_db_path = "test_inventory.db"

    flask_app.config.update({
        "TESTING": True,
        "DATABASE": test_db_path
    })
    
    with flask_app.app_context():
        db = get_db()
        cur = db.cursor()

        print(f"Using test database: {flask_app.config['DATABASE']}")  # Debug print

        # Read schema.sql and execute it
        with open("schema.sql", "r") as schema:
            schema_sql = schema.read()
            print("Executing schema.sql...")
            cur.executescript(schema_sql)

        # Read data.sql and execute it (if exists)
        if os.path.exists("data.sql"):
            with open("data.sql", "r") as data:
                data_sql = data.read()
                print("Executing data.sql...")
                cur.executescript(data_sql)

        db.commit()


    yield flask_app

    with flask_app.app_context():
        db= get_db()
        db.close()

    if os.path.exists(test_db_path):
        os.remove(test_db_path)
#teardown
@pytest.fixture()
def client(app):
    return app.test_client()

