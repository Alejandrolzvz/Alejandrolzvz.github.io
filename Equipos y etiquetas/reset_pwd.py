from backend.database import SQLALCHEMY_DATABASE_URL
from backend.models import Base, User
from backend.auth import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)

session = Session()
admin_user = session.query(User).filter_by(username="admin").first()
if admin_user:
    admin_user.hashed_password = get_password_hash("admin123")
    admin_user.is_superadmin = True
    admin_user.is_admin = True
    session.commit()
    print("Admin user found and reset to 'admin123'")
else:
    print("Admin user not found. Creating...")
    hashed_pw = get_password_hash("admin123")
    new_admin = User(username="admin", hashed_password=hashed_pw, is_superadmin=True, is_admin=True)
    session.add(new_admin)
    session.commit()
    print("Admin user created with 'admin123'")
session.close()
