from utils.db import get_db_connection
c = get_db_connection()
print(c.execute('PRAGMA table_info(users)').fetchall())
