import sys
from dotenv import load_dotenv
load_dotenv('backend/.env')
sys.path.append('backend')
from app.database import SessionLocal
from app.models.domain import User
from app.core.security import verify_password
import bcrypt

db = SessionLocal()
u = db.query(User).filter(User.email=="patient@email.com").first()
print(f"User: {u.email}")
res = verify_password("password123", u.hashed_password)
print(f"Does 'password123' match the hash in db? {res}")
db.close()
