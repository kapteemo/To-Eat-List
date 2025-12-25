"""Verify dashboard buttons hit intended URLs and return 200 for an authenticated session.

This script uses Flask's test_client to simulate a logged-in user.
"""
from app import app, DB_PATH
import sqlite3
from pathlib import Path

# Ensure a test user exists
conn = sqlite3.connect(str(DB_PATH))
conn.execute("PRAGMA foreign_keys = ON;")
c = conn.cursor()
# create a simple user if none exists
c.execute("SELECT id FROM users LIMIT 1")
row = c.fetchone()
if row is None:
    c.execute("INSERT INTO users (username, hash) VALUES (?, ?)", ("testuser", "x"))
    conn.commit()
    user_id = c.lastrowid
else:
    user_id = row[0]
conn.close()

with app.test_client() as client:
    # set session user_id
    with client.session_transaction() as sess:
        sess['user_id'] = user_id

    urls = ['/dashboard', '/create', '/mylists', '/random']
    for u in urls:
        resp = client.get(u)
        print(f"GET {u} -> {resp.status_code}")

print("Verification complete.")
