"""Call /random_pick 10 times using Flask test client to verify randomness and stability."""
from app import app, DB_PATH
import sqlite3

# ensure we have a user
conn = sqlite3.connect(str(DB_PATH))
conn.execute("PRAGMA foreign_keys = ON;")
c = conn.cursor()
c.execute("SELECT id FROM users LIMIT 1")
row = c.fetchone()
if row is None:
    c.execute("INSERT INTO users (username, hash) VALUES (?, ?)", ("verify_user", "x"))
    conn.commit()
    user_id = c.lastrowid
else:
    user_id = row[0]
conn.close()

results = []
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_id'] = user_id

    for i in range(10):
        r = client.get('/random_pick')
        print(f'Call {i+1}: status={r.status_code}')
        if r.status_code == 200:
            # crude parsing: find the food in the response body
            body = r.get_data(as_text=True)
            # naive extraction between id="random-food"> and </p>
            start = body.find('id="random-food"')
            food = None
            if start != -1:
                # find > after id
                gt = body.find('>', start)
                if gt != -1:
                    end = body.find('<', gt+1)
                    if end != -1:
                        food = body[gt+1:end].strip()
            results.append(food)
        else:
            results.append(None)

print('\nResults:')
for i, f in enumerate(results, 1):
    print(f'{i}: {f}')

print('\nUnique picks:', len(set([r for r in results if r])))
print('Verification complete.')
