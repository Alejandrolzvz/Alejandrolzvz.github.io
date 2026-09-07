from utils.db import get_db_connection
from werkzeug.security import generate_password_hash

conn = get_db_connection()
cursor = conn.cursor()

users_to_add = [
    ('PRODPlanta_A', 'prodacia123'),
    ('PRODELEC', 'prodelec123')
]

for username, pwd in users_to_add:
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if not cursor.fetchone():
        hashed = generate_password_hash(pwd)
        cursor.execute("INSERT INTO users (username, password_hash, role, role_id) VALUES (?, ?, ?, ?)", (username, hashed, 'PRODUC', 2))
        print(f"User {username} created.")
    else:
        print(f"User {username} already exists.")

conn.commit()
conn.close()
