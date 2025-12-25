#!/usr/bin/env python3
"""Seed script to populate global_random_foods in an SQLite DB.

Creates the schema if missing, cleans the global_random_foods table,
inserts 100 diverse food items, and verifies the row count.
"""
from pathlib import Path
import sqlite3
import sys

DB_PATH = Path(__file__).parent / "to_eat.db"

FOOD_ITEMS = [
    "Sushi",
    "Ramen",
    "Tempura",
    "Sashimi",
    "Onigiri",
    "Takoyaki",
    "Okonomiyaki",
    "Udon",
    "Soba",
    "Yakitori",
    "Tacos",
    "Burrito",
    "Quesadilla",
    "Enchiladas",
    "Nachos",
    "Pad Thai",
    "Green Curry",
    "Massaman Curry",
    "Tom Yum Soup",
    "Pho",
    "Banh Mi",
    "Spring Rolls",
    "Baozi",
    "Dim Sum",
    "Peking Duck",
    "Hot Pot",
    "Char Siu",
    "Yangzhou Fried Rice",
    "Samosa",
    "Biryani",
    "Butter Chicken",
    "Naan",
    "Palak Paneer",
    "Dosa",
    "Chole",
    "Masala Chai",
    "Falafel",
    "Hummus",
    "Shawarma",
    "Kebab",
    "Dolma",
    "Tabbouleh",
    "Shakshuka",
    "Couscous",
    "Tagine",
    "Jollof Rice",
    "Injera",
    "Doro Wat",
    "Bobotie",
    "Feijoada",
    "Ceviche",
    "Empanada",
    "Arepa",
    "Poutine",
    "Shepherd's Pie",
    "Fish and Chips",
    "Pierogi",
    "Goulash",
    "Wiener Schnitzel",
    "Pretzel",
    "Bratwurst",
    "Paella",
    "Tapas",
    "Pizza Margherita",
    "Lasagna",
    "Spaghetti Carbonara",
    "Risotto",
    "Gelato",
    "Tiramisu",
    "Cannoli",
    "Croissant",
    "Baguette",
    "Crepe",
    "Quiche Lorraine",
    "Ratatouille",
    "Bouillabaisse",
    "Coq au Vin",
    "Polenta",
    "Minestrone",
    "Caprese Salad",
    "Caesar Salad",
    "Gazpacho",
    "Kimchi",
    "Bibimbap",
    "Bulgogi",
    "Mapo Tofu",
    "Kung Pao Chicken",
    "Chow Mein",
    "Congee",
    "Mango Sticky Rice",
    "Mochi",
    "Nikujaga",
    "Shish Taouk",
    "Koshari",
    "Khachapuri",
    "Borscht",
    "Blini",
    "Churros",
    "Alfajores",
    "Baklava",
]


SCHEMA_SQL = """
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
"""


def main():
    if len(FOOD_ITEMS) != 100:
        print(f"ERROR: expected 100 food items, found {len(FOOD_ITEMS)}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        # Ensure schema exists
        cur.executescript(SCHEMA_SQL)

        # Clean target table to avoid duplicates on re-run
        cur.execute("DELETE FROM global_random_foods;")

        # Insert items
        insert_sql = "INSERT INTO global_random_foods (food_name, cuisine_type) VALUES (?, ?);"
        for name in FOOD_ITEMS:
            cur.execute(insert_sql, (name, None))

        conn.commit()

        # Verification
        cur.execute("SELECT COUNT(*) FROM global_random_foods;")
        (count,) = cur.fetchone()
        if count == len(FOOD_ITEMS):
            print("Database initialized successfully with 100 items.")
        else:
            print(f"Warning: expected {len(FOOD_ITEMS)} items but found {count} rows.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
