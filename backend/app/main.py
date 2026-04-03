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
from app.schemas import (
    PatientOnboardRequest, PatientOnboardResponse, Token, LoginRequest, DoctorRegisterRequest,
    AdaptationResponse, PatientDashboardResponse, DoctorDashboardResponse,
    SessionSummary, PatientListSummary
)
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from app.services.llm_service import generate_patient_feedback
from app.services.telemetry_service import start_session, log_repetition
from app.services.adaptation_engine import evaluate_patient_adaptation
from app.services.analytics_service import get_patient_dashboard, get_doctor_dashboard

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

@app.post("/api/auth/register-doctor", response_model=Token, tags=["auth"])
def register_doctor(payload: DoctorRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new Doctor in the system so they can log in via the portal."""
    existing_user = db.query(domain.User).filter(domain.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pw = get_password_hash(payload.password)
    new_user = domain.User(
        email=payload.email,
        hashed_password=hashed_pw,
        role="doctor",
        first_name=payload.first_name,
        last_name=payload.last_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-login after registration
    access_token = create_access_token(subject=str(new_user.id), role=new_user.role)
    return {"access_token": access_token, "token_type": "bearer", "role": new_user.role, "user_id": new_user.id}

@app.post("/api/auth/login", response_model=Token, tags=["auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Query database for user
    user = db.query(domain.User).filter(domain.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
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
            doctor_id=payload.doctor_id, # Safely inherited from the payload when auth token validates
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
# ANALYTICS & DASHBOARDS REST API
# ==========================================
@app.get("/api/patients/{user_id}/dashboard", response_model=PatientDashboardResponse, tags=["analytics"])
def read_patient_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the clinical summary, latest performance metrics, and adaptation status for a given patient.
    """
    response = get_patient_dashboard(db, user_id=user_id)
    if not response:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    return response

@app.get("/api/doctors/{doctor_id}/dashboard", response_model=DoctorDashboardResponse, tags=["analytics"])
def read_doctor_dashboard(doctor_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all assigned patients, evaluating their telemetry metrics to flag 'needs attention' risk pools.
    """
    response = get_doctor_dashboard(db, doctor_user_id=doctor_id)
    if not response:
        raise HTTPException(status_code=404, detail="Doctor user not found.")
    return response

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

    # 1.5 Load their specific Golden Rep Active Prescription created by the Doctor
    from sqlalchemy import desc
    current_rx = db.query(domain.ExercisePrescription).filter(
        domain.ExercisePrescription.patient_id == patient_id,
        domain.ExercisePrescription.exercise_type == "squat"
    ).order_by(desc(domain.ExercisePrescription.created_at)).first()

    # Use their clinical target, fallback to generic 100 degrees if not found
    target_rom_degrees = current_rx.target_rom_degrees if current_rx else 100.0
    engagement_threshold = min(140.0, target_rom_degrees + 30.0) # Start mapping rep when they drop into the prescribed zone
    target_reps = current_rx.reps_per_set if current_rx else 10

    # 2. Spin up our Deep Learning Brains for this session
    exercise = "squat" # This could be dynamically requested via URL parameter later
    buffer = TemporalBuffer(maxlen=30)
    expert_lstm = LSTMEngine(exercise=exercise)

    # 2.5 Initialize PostgreSQL Telemetry Logger for the Doctor's Portal
    telemetry_session = start_session(db, patient_id, exercise)
    rep_count = 0
    is_in_rep = False
    is_fatigued = False
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
            
            # --- 2-WAY PATIENT VOICE COMMUNICATION TRAP ---
            if "patient_vocal_command" in features:
                patient_quote = features["patient_vocal_command"]
                accumulated_errors.append({
                    "type": "Patient Verbal Intervention",
                    "severity": 1.0,
                    "clinical_target": "Listen to Patient",
                    "achieved": f"Patient said: '{patient_quote}'"
                })
                
                # Generate an immediate, empathetic AI response based on what they said
                vocal_response = await generate_patient_feedback(
                    patient_first_name=patient_name,
                    exercise=exercise,
                    current_rep=rep_count,
                    target_reps=target_reps,
                    errors=accumulated_errors,
                    is_fatigued=False,
                    fatigue_metrics=None
                )
                
                await websocket.send_json({
                    "status": "tracking",
                    "lstm_confidence": 1.0,
                    "errors": accumulated_errors,
                    "llm_feedback": vocal_response,
                    "rep_count": rep_count
                })
                
                # Pause briefly so AI can speak without tracking overlap
                await asyncio.sleep(3)
                continue

            # 4. Math extraction and ML Buffering
            if "left_knee_angle" not in features:
                continue
                
            current_knee_angle = (features["left_knee_angle"] + features["right_knee_angle"]) / 2.0
            buffer.add(features)
            seq = buffer.get_lstm_sequence()

            if seq is not None and len(seq) == buffer.history.maxlen:
                # 5. Continuous AI monitoring
                analysis_result = expert_lstm.analyze(seq)
                errors = analysis_result.get("errors", [])
                lstm_confidence = analysis_result.get("confidence", 0.95)
                
                # Squat going down -> Started a Rep!
                if current_knee_angle < engagement_threshold:
                    is_in_rep = True
                    if current_knee_angle < lowest_knee_angle:
                        lowest_knee_angle = current_knee_angle

                # Squat coming back up -> Rep Completed!
                elif current_knee_angle > 160 and is_in_rep:
                    rep_count += 1
                    
                    # Check if they failed to reach their Doctor's prescribed Golden Rep target depth
                    if lowest_knee_angle > target_rom_degrees:
                        accumulated_errors.append({
                            "type": "Insufficient Depth",
                            "severity": round((lowest_knee_angle - target_rom_degrees) / 10.0, 2),
                            "clinical_target": target_rom_degrees,
                            "achieved": round(lowest_knee_angle, 2)
                        })

                    # Compute Rep Form Score for fatigue tracking
                    rep_penalty = sum([err.get("severity", 0.5) * 5 for err in accumulated_errors])
                    rep_form_score = max(0.0, 100.0 - rep_penalty * 4)
                    buffer.add_rep_metric(lowest_knee_angle, rep_form_score)
                    
                    # Check Fatigue (Mid-Session Intervention)
                    is_fatigued, fatigue_metrics = buffer.check_fatigue_degradation(window=3, threshold=15.0)
                    if is_fatigued and rep_count < target_reps:
                        target_reps = rep_count  # End session early
                        accumulated_errors.append({
                            "type": "Session Interrupted: Muscular Fatigue Detected",
                            "severity": 1.0,
                            "clinical_target": "Safe Continuation",
                            "achieved": "Degraded Form"
                        })
                        last_llm_response_for_rep = await generate_patient_feedback(
                            patient_first_name=patient_name,
                            exercise=exercise,
                            current_rep=rep_count,
                            target_reps=target_reps,
                            errors=accumulated_errors,
                            is_fatigued=True,
                            fatigue_metrics=fatigue_metrics
                        )
                    elif accumulated_errors:
                        last_llm_response_for_rep = await generate_patient_feedback(
                            patient_first_name=patient_name,
                            exercise=exercise,
                            current_rep=rep_count,
                            target_reps=target_reps,
                            errors=accumulated_errors,
                            is_fatigued=False,
                            fatigue_metrics=None
                        )

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

                if errors:
                    # Append new distinct errors to the current rep tracking
                    for err in errors:
                        if not any(e["type"] == err["type"] for e in accumulated_errors):
                            accumulated_errors.append(err)

                response_payload = {
                    "status": "tracking",
                    "lstm_confidence": lstm_confidence,
                    "errors": errors,
                    "llm_feedback": last_llm_response_for_rep if last_llm_response_for_rep else None,
                    "rep_count": rep_count
                }

                # 7. Only generate conversational LLM feedback if there are errors and outside cooldown
                current_time = time.time()
                if last_llm_response_for_rep:
                    last_llm_time = current_time # Reset cooldown to prioritize the fatigue/rep completion message
                elif errors and (current_time - last_llm_time > feedback_cooldown):
                    natural_response = await generate_patient_feedback(
                        patient_first_name=patient_name,
                        exercise=exercise,
                        current_rep=rep_count,
                        target_reps=target_reps,
                        errors=errors,
                        is_fatigued=False,
                        fatigue_metrics=None
                    )
                    response_payload["llm_feedback"] = natural_response
                    last_llm_response_for_rep = natural_response # save to log in DB at end of rep
                    last_llm_time = current_time

                await websocket.send_json(response_payload)
                
                # Clear the message AFTER sending it to React so we don't spam TTS every frame
                if response_payload.get("llm_feedback") and not is_fatigued:
                     last_llm_response_for_rep = ""

                # Check for session completion
                if rep_count >= target_reps:
                    try:
                        new_rx = evaluate_patient_adaptation(db, patient_id, exercise)
                        await websocket.send_json({
                            "status": "completed",
                            "message": "Workout finished.",
                            "llm_feedback": "Workout complete. Saving your clinical progress."
                        })
                    except Exception as e:
                        print(f"Error completing session: {e}")

                    await asyncio.sleep(2) # Give frontend enough time to read the message and speak BEFORE closing
                    await websocket.close()
                    break # Terminate session loop cleanly
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
        import traceback
        traceback.print_exc()
        print(f"Tracking error: {e}")
        try:
            await websocket.close()
        except:
            pass

# =========================================================
# CUSTOM EXERCISE ENDPOINTS
# =========================================================

from app.schemas import CustomExerciseCreate, CustomExerciseResponse
from config.calibration_manager import CalibrationManager

@app.post("/api/exercises/custom", response_model=CustomExerciseResponse)
def create_custom_exercise(
    payload: CustomExerciseCreate,
    db: Session = Depends(get_db),
    current_token: str = Depends(oauth2_scheme)
):
    current_user = get_user_from_token(db, current_token)
    if not current_user or current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create novel exercises.")
        
    identifier = f"{current_user.id}_{payload.name.lower().replace(' ', '_')}_{int(time.time())}"
    
    nuevo = domain.CustomExercise(
        doctor_id=current_user.id,
        name=payload.name,
        identifier=identifier,
        tracked_angles=payload.tracked_angles
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    
    # Save the 3D analytical dataset to our configuration system
    cm = CalibrationManager()
    cm.save_golden_rep(identifier, payload.golden_rep_data)
    
    return CustomExerciseResponse(
        id=nuevo.id,
        name=nuevo.name,
        identifier=nuevo.identifier,
        tracked_angles=nuevo.tracked_angles,
        created_at=nuevo.created_at
    )

@app.get("/api/exercises/custom", response_model=list[CustomExerciseResponse])
def list_custom_exercises(
    db: Session = Depends(get_db),
    current_token: str = Depends(oauth2_scheme)
):
    current_user = get_user_from_token(db, current_token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    return db.query(domain.CustomExercise).all()  # Allow patients to see them too if assigned

# =========================================================
# WEBRTC SIGNALING SERVER (VIRTUAL CLINIC ROOMS)
# =========================================================

# Rooms dictionary to hold {room_id: {client_id: websocket}}
webrtc_rooms = {}

@app.websocket("/ws/signaling/{room_id}/{client_id}")
async def signaling_endpoint(websocket: WebSocket, room_id: str, client_id: str):
    await websocket.accept()
    
    if room_id not in webrtc_rooms:
        webrtc_rooms[room_id] = {}
        
    webrtc_rooms[room_id][client_id] = websocket
    
    try:
        while True:
            # Receive WebRTC signaling data (Offer, Answer, ICE Candidates)
            data = await websocket.receive_text()
            
            # Broadcast the WebRTC signaling data to everyone else in the room
            for cid, conn in webrtc_rooms[room_id].items():
                if cid != client_id:
                    try:
                        await conn.send_text(data)
                    except:
                        pass
    except WebSocketDisconnect:
        if room_id in webrtc_rooms and client_id in webrtc_rooms[room_id]:
            del webrtc_rooms[room_id][client_id]
            if len(webrtc_rooms[room_id]) == 0:
                del webrtc_rooms[room_id]
    except Exception as e:
        print(f"WebRTC Signaling Exception: {e}")
        if room_id in webrtc_rooms and client_id in webrtc_rooms[room_id]:
            del webrtc_rooms[room_id][client_id]

