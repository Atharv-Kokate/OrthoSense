from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import domain

def evaluate_patient_adaptation(db: Session, patient_id: int, exercise_type: str = "squat"):
    """
    Auto-Adaptation Engine Rules: 
    Analyzes the most recent session's performance against the active prescription.
    If the patient excels, progress the difficulty. If they struggle, regress it.
    Returns the new prescription, or None if no adaptation was needed.
    """
    # 1. Fetch current active prescription for exercise type
    current_rx = db.query(domain.ExercisePrescription).filter(
        domain.ExercisePrescription.patient_id == patient_id,
        domain.ExercisePrescription.exercise_type == exercise_type
    ).order_by(desc(domain.ExercisePrescription.created_at)).first()

    if not current_rx or not current_rx.auto_adaptive:
        return None

    # 2. Fetch the patient's most recent completed telemetry session for this exercise
    latest_session = db.query(domain.TelemetrySession).filter(
        domain.TelemetrySession.patient_id == patient_id,
        domain.TelemetrySession.exercise_type == exercise_type,
        domain.TelemetrySession.total_reps_completed > 0
    ).order_by(desc(domain.TelemetrySession.session_date)).first()

    if not latest_session:
        return None

    # 3. Fetch repetition logs for that session to calculate detailed performance
    rep_logs = db.query(domain.RepetitionLog).filter(
        domain.RepetitionLog.session_id == latest_session.id
    ).all()

    if not rep_logs:
        return None

    valid_roms = [rep.max_rom_achieved for rep in rep_logs if rep.max_rom_achieved is not None]
    avg_rom = sum(valid_roms) / len(valid_roms) if valid_roms else 0.0

    # 4. Extract Key Performance Indicators (KPIs)
    target_rom = current_rx.target_rom_degrees or 0.0
    target_reps = current_rx.reps_per_set or 10
    actual_reps = latest_session.total_reps_completed
    form_score = latest_session.overall_form_score

    # Fetch patient for personalized demographics
    patient = db.query(domain.PatientProfile).filter(domain.PatientProfile.id == patient_id).first()
    days_post_op = 14
    if patient and patient.date_of_surgery:
        import datetime
        dt_surgery = patient.date_of_surgery.replace(tzinfo=datetime.timezone.utc)
        days_post_op = (datetime.datetime.now(datetime.timezone.utc) - dt_surgery).days
        
    prog_threshold = 85.0
    regress_threshold = 60.0
    rom_increment = 5.0
    reps_increment = 2
    
    if days_post_op < 14:
        # Acute inflammatory phase, be extremely conservative
        prog_threshold = 92.0
        regress_threshold = 70.0
        rom_increment = 2.0
        reps_increment = 1
    elif days_post_op > 60:
        # Strengthening phase: push harder
        prog_threshold = 80.0
        regress_threshold = 55.0
        rom_increment = 10.0
        reps_increment = 3

    new_target_rom = target_rom
    new_reps_per_set = target_reps
    needs_update = False
    audit_reason = "No change"

    # 5. Core Algorithmic Adaptation Rules
    # Case A: Progression (They crushed it: perfect form, enough reps, hit full ROM)
    if form_score >= prog_threshold and actual_reps >= target_reps and avg_rom >= (target_rom - 5.0):
        if target_rom < 120.0:  # Assuming maximum healthy knee flexion context
            new_target_rom += rom_increment
            audit_reason = f"Progressed ROM by {rom_increment}° due to high form score ({form_score}%) in phase > {days_post_op} days."
        elif target_reps < 15:
            new_reps_per_set += reps_increment
            audit_reason = f"Progressed Reps by {reps_increment} due to high form score ({form_score}%) in phase > {days_post_op} days."
        needs_update = True

    # Case B: Regression (They struggled: poor form, failed reps, or restricted ROM)
    elif form_score < regress_threshold or avg_rom < (target_rom - 15.0):
        if target_rom > 60.0:
            new_target_rom -= 10.0
            audit_reason = f"Regressed ROM by 10° due to low form score ({form_score}%) or restricted motion."
        elif target_reps > 5:
            new_reps_per_set -= 2
            audit_reason = f"Regressed Reps by 2 due to low form score ({form_score}%)."
        needs_update = True

    # 6. Apply New Prescription to Database if Changed
    if needs_update and (new_target_rom != target_rom or new_reps_per_set != target_reps):
        new_rx = domain.ExercisePrescription(
            patient_id=patient_id,
            exercise_type=exercise_type,
            target_rom_degrees=new_target_rom,
            reps_per_set=new_reps_per_set,
            sets_per_day=current_rx.sets_per_day,
            auto_adaptive=True,
            adaptation_reason=audit_reason
        )
        db.add(new_rx)
        db.commit()
        db.refresh(new_rx)
        return new_rx
    
    return None
