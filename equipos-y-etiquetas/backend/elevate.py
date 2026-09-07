import os
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
from models import Base, User
from sqlalchemy.orm import sessionmaker

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)

def update_db():
    Base.metadata.create_all(bind=engine)
    
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            print("Added is_admin to users")
        except Exception as e:
            print("is_admin might already exist:", e)

    session = Session()
    admin_user = session.query(User).filter_by(username="admin").first()
    if admin_user:
        admin_user.is_superadmin = True
        admin_user.is_admin = True
        session.commit()
        print("Elevated admin to superadmin and admin")
    else:
        print("Admin user not found")
    session.close()

if __name__ == "__main__":
    update_db()
