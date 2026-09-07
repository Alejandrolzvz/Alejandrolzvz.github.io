from backend.database import SQLALCHEMY_DATABASE_URL
from backend.models import Base, User
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)

def update_db():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT TRUE"))
            print("Added must_change_password to users")
        except Exception as e:
            print("must_change_password might already exist:", e)

    session = Session()
    admin_user = session.query(User).filter_by(username="admin").first()
    if admin_user:
        admin_user.must_change_password = False
        session.commit()
        print("Set must_change_password to False for 'admin'")
    session.close()

if __name__ == "__main__":
    update_db()
