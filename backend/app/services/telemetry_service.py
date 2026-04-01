from sqlalchemy.orm import Session
from app.models import domain

def start_session(db: Session, patient_id: int, exercise_type: str):
    """Initializes a new tracking session in the database."""
    session_db = domain.TelemetrySession(
        patient_id=patient_id,
        exercise_type=exercise_type,
        total_reps_completed=0,
        overall_form_score=100.0  # Starts at 100%, lowers based on severe errors
    )
    db.add(session_db)
    db.commit()
    db.refresh(session_db)
    return session_db

def log_repetition(db: Session, session_id: int, rep_number: int, max_rom_achieved: float, errors: list, ai_feedback: str):
    """
    Logs the exact biometric results of a single repetition safely into the PostgreSQL database.
    This creates an immutable medical record.
    """
    rep_log = domain.RepetitionLog(
        session_id=session_id,
        rep_number=rep_number,
        max_rom_achieved=round(max_rom_achieved, 2),
        errors_detected=errors,
        ai_feedback_given=ai_feedback
    )
    db.add(rep_log)

    # Automatically dynamically downgrade the overall session score based on errors
    session_db = db.query(domain.TelemetrySession).filter(domain.TelemetrySession.id == session_id).first()
    if session_db:
        session_db.total_reps_completed = rep_number
        if errors:
            # Deduct points for the presence of errors (scalable penalty logic)
            penalty = sum([err.get("severity", 0.5) * 5 for err in errors])
            session_db.overall_form_score = max(0.0, session_db.overall_form_score - penalty)
            
    db.commit()
    db.refresh(rep_log)
    return rep_log
