import sys
from dotenv import load_dotenv
load_dotenv('backend/.env')
sys.path.append('backend')
from app.database import SessionLocal
from app.models.domain import User
from sqlalchemy import text

db = SessionLocal()
con = db.connection()
res = con.execute(text("SELECT id, email, role, length(email), length(hashed_password) FROM users"))
for row in res:
    print(row)
db.close()
