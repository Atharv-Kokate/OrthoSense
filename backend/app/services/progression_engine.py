from sqlalchemy.orm import Session
from app.models.domain import (
    PatientProgram, ProgramPhase, PhaseExercise, PhaseProgressionRule,
    TelemetrySession, RehabProgram
)

def evaluate_macro_progression(db: Session, patient_id: int):
    # Get active patient program
    patient_prog = db.query(PatientProgram).filter(
        PatientProgram.patient_id == patient_id,
        PatientProgram.is_ready_for_next_phase == False
    ).first()
    
    if not patient_prog:
        return {"status": "no_active_program_or_already_ready"}

    # Get progression rules for current phase
    rules = db.query(PhaseProgressionRule).filter(
        PhaseProgressionRule.phase_id == patient_prog.current_phase_id
    ).all()
    
    if not rules:
        return {"status": "no_rules_found"}

    # Need rule logic - currently simplistic
    sessions = db.query(TelemetrySession).filter(
        TelemetrySession.patient_id == patient_id
    ).order_by(TelemetrySession.session_date.desc()).limit(1).all()

    if not sessions:
        return {"status": "no_sessions"}
        
    s = sessions[0]
    
    all_passed = True
    for rule in rules:
        # Example logic checking form score vs rule
        # You'll enhance this part
        if rule.metric == 'avg_form_score':
            if rule.operator == '>=' and s.overall_form_score >= rule.target_value:
                continue
            all_passed = False

    if all_passed:
        patient_prog.is_ready_for_next_phase = True
        db.commit()
        return {"status": "ready_for_promotion", "phase_id": patient_prog.current_phase_id}

    return {"status": "not_ready"}