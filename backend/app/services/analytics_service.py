from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from app.models import domain
from app.schemas import SessionSummary, PatientListSummary, PatientDashboardResponse, DoctorDashboardResponse

def get_patient_dashboard(db: Session, user_id: int) -> PatientDashboardResponse:
    """Aggregates all clinical analytics for a specific patient."""
    
    # 1. Extract User info first to find their mapped profile
    user = db.query(domain.User).filter(domain.User.id == user_id).first()
    if not user:
        return None
        
    patient = db.query(domain.PatientProfile).filter(domain.PatientProfile.user_id == user_id).first()
    if not patient:
        return None
    
    patient_id = patient.id
    full_name = f"{user.first_name} {user.last_name}"
    
    # 3. Current active prescription
    current_rx = db.query(domain.ExercisePrescription).filter(
        domain.ExercisePrescription.patient_id == patient_id
    ).order_by(desc(domain.ExercisePrescription.created_at)).first()
    
    target_rom = current_rx.target_rom_degrees if current_rx else 0.0
    reps_per_set = current_rx.reps_per_set if current_rx else 0
    
    # 4. Recent Telemetry Sessions (Max 10)
    sessions_db = db.query(domain.TelemetrySession).filter(
        domain.TelemetrySession.patient_id == patient_id,
        domain.TelemetrySession.total_reps_completed > 0
    ).order_by(desc(domain.TelemetrySession.session_date)).limit(10).all()
    
    recent_sessions = []
    for s in sessions_db:
        recent_sessions.append(SessionSummary(
            session_id=s.id,
            session_date=s.session_date,
            total_reps_completed=s.total_reps_completed,
            overall_form_score=s.overall_form_score
        ))

    # 5. Last 7 Days Avg Form Score
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_scores = db.query(domain.TelemetrySession.overall_form_score).filter(
        domain.TelemetrySession.patient_id == patient_id,
        domain.TelemetrySession.session_date >= week_ago,
        domain.TelemetrySession.total_reps_completed > 0
    ).all()
    
    avg_score = sum([s[0] for s in recent_scores]) / len(recent_scores) if recent_scores else 0.0
    
    return PatientDashboardResponse(
        patient_id=patient_id,
        patient_name=full_name,
        condition=patient.condition or "Unknown",
        current_target_rom=target_rom,
        current_reps_per_set=reps_per_set,
        recent_sessions=recent_sessions,
        average_form_score_7d=round(avg_score, 2),
        adaptation_reason=current_rx.adaptation_reason if current_rx and hasattr(current_rx, "adaptation_reason") else None
    )

def get_doctor_dashboard(db: Session, doctor_user_id: int) -> DoctorDashboardResponse:
    """Aggregates all active patients assigned to a specific doctor."""
    
    # Check Doctor Profile
    doctor_user = db.query(domain.User).filter(domain.User.id == doctor_user_id).first()
    if not doctor_user:
        return None
        
    doc_name = f"Dr. {doctor_user.last_name}" if doctor_user and doctor_user.last_name else "Doctor"
    
    # Find assigned patient profiles
    patients_assigned = db.query(domain.PatientProfile).filter(
        domain.PatientProfile.doctor_id == doctor_user_id
    ).all()

    patient_summaries = []
    for p in patients_assigned:
        user_record = db.query(domain.User).filter(domain.User.id == p.user_id).first()
        full_name = f"{user_record.first_name} {user_record.last_name}" if user_record else "Unknown Profile"
        
        # Latest session metric
        last_s = db.query(domain.TelemetrySession).filter(
            domain.TelemetrySession.patient_id == p.id,
            domain.TelemetrySession.total_reps_completed > 0
        ).order_by(desc(domain.TelemetrySession.session_date)).first()
        
        needs_attn = False
        if last_s:
            # Alert if last score was critically low
            needs_attn = last_s.overall_form_score < 70.0
            last_date = last_s.session_date
        else:
            # Alert if no sessions done yet
            needs_attn = True
            last_date = None
            
        patient_summaries.append(PatientListSummary(
            patient_profile_id=p.id,
            patient_name=full_name,
            condition=p.condition,
            latest_session_date=last_date,
            needs_attention=needs_attn
        ))

    return DoctorDashboardResponse(
        doctor_id=doctor_user_id,
        doctor_name=doc_name,
        total_active_patients=len(patient_summaries),
        patients=patient_summaries
    )
