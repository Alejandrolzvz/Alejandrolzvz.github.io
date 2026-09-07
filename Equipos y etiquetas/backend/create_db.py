import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_db(password):
    try:
        con = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password=password)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute('CREATE DATABASE equipos_db')
        cur.close()
        con.close()
        print("Database 'equipos_db' created successfully.")
    except psycopg2.errors.DuplicateDatabase:
        print("Database 'equipos_db' already exists.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    pwd = sys.argv[1] if len(sys.argv) > 1 else "postgres"
    create_db(pwd)
