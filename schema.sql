CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
);

CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    start_date TEXT,
    end_date TEXT
);

CREATE TABLE stops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER,
    city TEXT,
    start_date TEXT,
    end_date TEXT,
    position INTEGER
);

CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stop_id INTEGER,
    name TEXT,
    cost INTEGER
);
