import sys
from dotenv import load_dotenv
load_dotenv('backend/.env')
sys.path.append('backend')
from app.database import SessionLocal
from app.models.domain import User
from app.core.security import verify_password
db = SessionLocal()
print("Number of users:", db.query(User).count())
u = db.query(User).filter(User.email=="patient@email.com").first()
print("Role:", u.role)
db.close()
