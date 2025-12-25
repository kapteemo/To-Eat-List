-- Database schema for to_eat_list
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS food_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    list_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS food_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    food_name TEXT NOT NULL,
    is_checked INTEGER NOT NULL DEFAULT 0 CHECK(is_checked IN (0,1)),
    FOREIGN KEY(list_id) REFERENCES food_lists(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS global_random_foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name TEXT NOT NULL,
    cuisine_type TEXT
);
