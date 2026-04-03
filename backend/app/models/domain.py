from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """Core platform user: Can be a Doctor or Patient."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) # 'doctor' or 'patient'
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PatientProfile(Base):
    """Patient specific demographic and medical data."""
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    doctor_id = Column(Integer, ForeignKey("users.id")) # Assigned doctor
    condition = Column(String)
    date_of_surgery = Column(DateTime)
    
    user = relationship("User", foreign_keys=[user_id])
    doctor = relationship("User", foreign_keys=[doctor_id])
    prescriptions = relationship("ExercisePrescription", back_populates="patient")
    sessions = relationship("TelemetrySession", back_populates="patient")
    specific_exercises = relationship("PatientSpecificExercise", back_populates="patient")

class PatientSpecificExercise(Base):
    """Dynamically recorded custom exercises linked explicitly to a specific patient, 
    complete with 3D skeleton data for replay."""
    __tablename__ = "patient_specific_exercises"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    
    name = Column(String, nullable=False)
    description = Column(String)
    
    # E.g. {"knee_angle": ["hip", "knee", "ankle"]}
    tracked_angles = Column(JSON, nullable=False)
    
    # 3D Tracking data to render the stick-figure & run DTW Engine
    golden_rep_data = Column(JSON, nullable=False) 
    
    target_rom_degrees = Column(Float, nullable=True)
    reps_per_set = Column(Integer, default=10)
    sets_per_day = Column(Integer, default=3)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="specific_exercises")
    doctor = relationship("User", foreign_keys=[doctor_id])

class CustomExercise(Base):
    """Dynamic exercises created by doctors via the no-code studio."""
    __tablename__ = "custom_exercises"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    identifier = Column(String, unique=True, index=True) # e.g., 'dr_smith_bicep_curl_1'
    tracked_angles = Column(JSON, nullable=False) # e.g., {"elbow_angle": ["left_shoulder", "left_elbow", "left_wrist"]}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor = relationship("User", foreign_keys=[doctor_id])

class ExercisePrescription(Base):
    """Dynamic targets set either by doctor manually or auto-adjusted by our AI."""
    __tablename__ = "exercise_prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    exercise_type = Column(String, nullable=False) # 'squat', 'lunge', etc.
    target_rom_degrees = Column(Float) # Target active angle (e.g., knee to 100)
    reps_per_set = Column(Integer, default=10)
    sets_per_day = Column(Integer, default=3)
    auto_adaptive = Column(Boolean, default=True) # Allows AI to upgrade/downgrade difficulty
    adaptation_reason = Column(String) # Audit trail for AI updates
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="prescriptions")

class TelemetrySession(Base):
    """A single tracking session where a patient performs exercises."""
    __tablename__ = "telemetry_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    exercise_type = Column(String, nullable=False)
    session_date = Column(DateTime(timezone=True), server_default=func.now())
    total_reps_completed = Column(Integer, default=0)
    overall_form_score = Column(Float, default=0.0)
    
    patient = relationship("PatientProfile", back_populates="sessions")
    reps = relationship("RepetitionLog", back_populates="session")

class RepetitionLog(Base):
    """Sub-second telemetry data representing a single analyzed repetition."""
    __tablename__ = "repetition_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("telemetry_sessions.id"))
    rep_number = Column(Integer)
    max_rom_achieved = Column(Float) # The deepest joint angle reached
    errors_detected = Column(JSON) # e.g. [{"type": "knee_caving", "severity": 0.95}]
    ai_feedback_given = Column(String) # What Groq told the patient
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("TelemetrySession", back_populates="reps")