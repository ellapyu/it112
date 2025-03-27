PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS macronutrient (
    id INTEGER PRIMARY KEY,
    macro_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS ingredient (
    id INTEGER PRIMARY KEY,
    ingredient_name TEXT UNIQUE NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY,
    quantity TEXT DEFAULT '1',
    last_updated TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    category_id INT NOT NULL,
    user_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(id)  ON DELETE CASCADE
);

--junction table for many to many -- allows for joins when querying inventory table
CREATE TABLE IF NOT EXISTS ingredient_macronutrient (
    ingredient_id INTEGER,
    macronutrient_id INTEGER,
    PRIMARY KEY (ingredient_id, macronutrient_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(id) ON DELETE CASCADE,
    FOREIGN KEY (macronutrient_id) REFERENCES macronutrient(id) ON DELETE CASCADE
);