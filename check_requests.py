import sys
from dotenv import load_dotenv
load_dotenv('backend/.env')
sys.path.append('backend')
from app.database import SessionLocal
from app.models.domain import User
from app.core.security import verify_password
import requests

response = requests.post("http://localhost:8000/api/auth/login", data={"username": "patient@email.com", "password": "password123"})
print(response.status_code)
print(response.json())
