from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ==================== AUTH ====================
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

# ==================== ONBOARDING ====================
class PatientOnboardRequest(BaseModel):
    """Schema for validating the Clinical Onboarding and Golden Rep data from the Nurse/Doctor Portal"""
    first_name: str
    last_name: str
    email: EmailStr
    condition: str
    date_of_surgery: str
    target_rom_degrees: float
    auto_adaptive: bool = True
    
    # In a full product, the doctor's ID would come from the JWT token
    doctor_id: Optional[int] = 1

class PatientOnboardResponse(BaseModel):
    status: str
    message: str
    patient_profile_id: int
    prescription_id: int
