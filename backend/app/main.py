import sys
import os
import json
import time
from datetime import datetime
from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError

from app.database import engine, Base, get_db
from app.models import domain
from app.schemas import PatientOnboardRequest, PatientOnboardResponse, Token, LoginRequest, AdaptationResponse
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from app.services.llm_service import generate_patient_feedback
from app.services.telemetry_service import start_session, log_repetition
from app.services.adaptation_engine import evaluate_patient_adaptation

# --- DYNAMICALLY LINK THE EXISTING AI MODELS ---
# By doing this, our FastAPI web server can use the 
# deep learning engine you've already built!
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from memory.temporal_buffer import TemporalBuffer
from diagnosis.lstm_engine import LSTMEngine
# -----------------------------------------------

# Automatically create all database tables if they don't exist
domain.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS so the React frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "OrthoSense Clinical AI Backend is alive."}

# ==========================================
# AUTHENTICATION & SECURITY DEPENEDENCIES
# ==========================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.query(domain.User).filter(domain.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/api/auth/login", response_model=Token, tags=["auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Query database for user
    user = db.query(domain.User).filter(domain.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # We mock Doctor authentication if it does not exist in DB yet for demo
        if form_data.username == 'doctor@orthosense.ai':
            access_token = create_access_token(subject=1, role="doctor")
            return {"access_token": access_token, "token_type": "bearer", "role": "doctor", "user_id": 1}
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "user_id": user.id}

# ==========================================
# CLINICAL ONBOARDING REST API
# ==========================================
@app.post("/api/patients/onboard", response_model=PatientOnboardResponse, tags=["clinical"])
def record_golden_rep_baseline(payload: PatientOnboardRequest, db: Session = Depends(get_db)):
    """
    Saves the supervised "Golden Rep" target angle into the patient's biological profile.
    This creates the User, PatientProfile, and their assigned ExercisePrescription.
    """
    # 1. Create a dummy password hash matching 'password123' so they can login later.
    hashed_pw = get_password_hash("password123")
    
    try:
        # 1. Create the Authentication User
        new_user = domain.User(
            email=payload.email,
            hashed_password=hashed_pw,
            role="patient",
            first_name=payload.first_name,
            last_name=payload.last_name
        )
        db.add(new_user)
        db.flush() # Flush to get the new_user.id
        
        # 2. Create the specific Patient Clinical Profile
        parsed_date = datetime.strptime(payload.date_of_surgery, "%Y-%m-%d")
        new_profile = domain.PatientProfile(
            user_id=new_user.id,
            doctor_id=payload.doctor_id, # Hardcoded ID 1 for now
            condition=payload.condition,
            date_of_surgery=parsed_date
        )
        db.add(new_profile)
        db.flush() # Flush to get new_profile.id

        # 3. Create their AI Exercise Target using the Golden Rep mathematical baseline
        new_prescription = domain.ExercisePrescription(
            patient_id=new_profile.id,
            exercise_type="squat", 
            target_rom_degrees=payload.target_rom_degrees,
            reps_per_set=10,
            sets_per_day=3,
            auto_adaptive=payload.auto_adaptive
        )
        db.add(new_prescription)
        db.flush() # Flush to get prescription ID
        
        # Commit the transaction safely
        db.commit()
        
        return PatientOnboardResponse(
            status="success",
            message="Golden Rep target safely stored into Clinical Database.",
            patient_profile_id=new_profile.id,
            prescription_id=new_prescription.id
        )
        
    except Exception as e:
        db.rollback()
        print(f"Error persisting golden baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# ADAPTATION ENGINE REST API
# ==========================================
@app.post("/api/patients/{patient_id}/adaptation/evaluate", response_model=AdaptationResponse, tags=["adaptation"])
def trigger_adaptation_evaluation(patient_id: int, exercise_type: str = "squat", db: Session = Depends(get_db)):
    """
    Evaluates the patient's performance based on their most recent session and adjusts target metrics if auto_adaptive is enabled.
    """
    try:
        new_rx = evaluate_patient_adaptation(db, patient_id, exercise_type)
        if new_rx:
            return AdaptationResponse(
                status="success",
                message="Exercise prescription dynamically adjusted based on recent session telemetry.",
                is_adapted=True,
                new_target_rom_degrees=new_rx.target_rom_degrees,
                new_reps_per_set=new_rx.reps_per_set
            )
        else:
            return AdaptationResponse(
                status="success",
                message="No adaptation required at this time based on performance rules.",
                is_adapted=False
            )
    except Exception as e:
        print(f"Error executing adaptation engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# PATIENT WEBSOCKET TELEMETRY ENGINE
# ==========================================
@app.websocket("/ws/track/{patient_id}")
async def websocket_endpoint(websocket: WebSocket, patient_id: int, db: Session = Depends(get_db)):
    """
    Main Telemetry Ingestion Engine:
    This WebSocket stays open. The React app streams coordinates at ~30 FPS.
    We push them into the Temporal Buffer, feed to BiLSTM, and stream feedback back.
    """
    await websocket.accept()
    
    # 1. Look up the patient to personalize LLM Feedback
    patient = db.query(domain.PatientProfile).filter(domain.PatientProfile.id == patient_id).first()
    patient_name = patient.user.first_name if (patient and patient.user) else "Guest"
    
    # 2. Spin up our Deep Learning Brains for this session
    exercise = "squat" # This could be dynamically requested via URL parameter later
    buffer = TemporalBuffer(maxlen=30)
    expert_lstm = LSTMEngine(exercise=exercise)
    
    # 2.5 Initialize PostgreSQL Telemetry Logger for the Doctor's Portal
    telemetry_session = start_session(db, patient_id, exercise)
    rep_count = 0
    is_in_rep = False
    lowest_knee_angle = 180.0
    accumulated_errors = [] # Store errors found during the current rep
    last_llm_response_for_rep = ""
    
    last_llm_time = 0
    feedback_cooldown = 4.0 # Do not overwhelm patient with voice feedback faster than 4 seconds
    
    try:
        while True:
            # 3. Receive 3D mathematical stream from React Browser Sensor
            raw_data = await websocket.receive_text()
            features = json.loads(raw_data)
            
            current_knee_angle = features.get("left_knee_angle", 180)
            
            # --- REAL-TIME REP COUNTING STATE MACHINE ---
            # Squat going down
            if current_knee_angle < 140:
                is_in_rep = True
                if current_knee_angle < lowest_knee_angle:
                    lowest_knee_angle = current_knee_angle
            
            # Squat coming back up -> Rep Completed!
            elif current_knee_angle > 160 and is_in_rep:
                rep_count += 1
                # Write to Medical Record Database!
                log_repetition(
                    db=db, 
                    session_id=telemetry_session.id, 
                    rep_number=rep_count, 
                    max_rom_achieved=lowest_knee_angle, 
                    errors=accumulated_errors, 
                    ai_feedback=last_llm_response_for_rep
                )
                
                # Reset rep state
                is_in_rep = False
                lowest_knee_angle = 180.0
                accumulated_errors = []
                last_llm_response_for_rep = ""
                
            # --------------------------------------------

            # 4. Add to continuous 1-second memory layer
            buffer.add(features)
            
            # 5. Extract fully processed Pandas DataFrame (with Velocities & Smooths)
            lstm_sequence = buffer.get_lstm_sequence()
            
            # 6. Execute Neural Inference!
            if expert_lstm.ready and lstm_sequence is not None:
                diagnosis = expert_lstm.analyze(lstm_sequence)
                errors = diagnosis.get("errors", [])
                
                if errors:
                    # Append new distinct errors to the current rep tracking
                    for err in errors:
                        if not any(e["type"] == err["type"] for e in accumulated_errors):
                            accumulated_errors.append(err)
                
                response_payload = {
                    "status": "tracking",
                    "lstm_confidence": 0.95,
                    "errors": errors,
                    "llm_feedback": None,
                    "rep_count": rep_count
                }
                
                # 7. Only generate conversational LLM feedback if there are errors and outside cooldown
                current_time = time.time()
                if errors and (current_time - last_llm_time > feedback_cooldown):
                    natural_response = generate_patient_feedback(patient_name, exercise, errors)
                    response_payload["llm_feedback"] = natural_response
                    last_llm_response_for_rep = natural_response # save to log in DB at end of rep
                    last_llm_time = current_time
                    
                await websocket.send_json(response_payload)
            else:
                # Buffer is still filling up (first 1 second)
                await websocket.send_json({"status": "buffering", "message": "Gathering AI baseline..."})
                
    except WebSocketDisconnect:
        print(f"Patient {patient_id} Tracking Session Ended cleanly.")
        
        # 🔥 Trigger the auto-adaptation engine automatically upon session completion!
        try:
            new_rx = evaluate_patient_adaptation(db, patient_id, "squat")
            if new_rx:
                print(f"✅ AI Engine dynamically prescribed new ROM: {new_rx.target_rom_degrees}° | Reps: {new_rx.reps_per_set} for Patient {patient_id}")
            else:
                print(f"ℹ️ AI Engine analyzed session for Patient {patient_id}. Existing prescription remains optimal.")
        except Exception as adapt_err:
            print(f"Adaptation Engine Execution Error safely caught: {adapt_err}")

    except Exception as e:
        print(f"Tracking error: {e}")
        try:
            await websocket.close()
        except:
            pass
