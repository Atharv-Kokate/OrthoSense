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

class DoctorRegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
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

    # Linked precisely to whoever is logged in and triggering the onboard    
    doctor_id: Optional[int] = None

class PatientOnboardResponse(BaseModel):
    status: str
    message: str
    patient_profile_id: int
    prescription_id: int

# ==================== ADAPTATION & TELEMETRY ====================
class AdaptationResponse(BaseModel):
    status: str
    message: str
    is_adapted: bool
    new_target_rom_degrees: Optional[float] = None
    new_reps_per_set: Optional[int] = None

# ==================== DASHBOARDS & ANALYTICS ====================
class SessionSummary(BaseModel):
    session_id: int
    session_date: datetime
    total_reps_completed: int
    overall_form_score: float

class PatientDashboardResponse(BaseModel):
    patient_id: int
    patient_name: str
    condition: str
    current_target_rom: float
    current_reps_per_set: int
    recent_sessions: List[SessionSummary]
    average_form_score_7d: float
    adaptation_reason: Optional[str] = None

class PatientListSummary(BaseModel):
    patient_profile_id: int
    patient_name: str
    condition: str
    latest_session_date: Optional[datetime] = None
    needs_attention: bool  # e.g., low form score or missed sessions

class DoctorDashboardResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    total_active_patients: int
    patients: List[PatientListSummary]

# ==================== CUSTOM EXERCISES ====================
class CustomExerciseCreate(BaseModel):
    name: str
    tracked_angles: dict # e.g., {"elbow_angle": ["left_shoulder", "left_elbow", "left_wrist"]}
    golden_rep_data: List[dict] # The array of 3D feature arrays recorded by the PT

class CustomExerciseResponse(BaseModel):
    id: int
    name: str
    identifier: str
    tracked_angles: dict
    created_at: datetime

# ==================== PATIENT SPECIFIC EXERCISES ====================

class PatientSpecificExerciseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tracked_angles: dict
    target_rom_degrees: Optional[float] = None
    reps_per_set: int = 10
    sets_per_day: int = 3
    golden_rep_data: List[dict]

class PatientSpecificExerciseResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    name: str
    description: Optional[str] = None
    tracked_angles: dict
    target_rom_degrees: Optional[float] = None
    reps_per_set: int
    sets_per_day: int
    created_at: datetime

    class Config:
        from_attributes = True

