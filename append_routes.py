import os

routes_to_append = '''
from app.models.domain import RehabProgram, ProgramPhase, PhaseExercise, PhaseProgressionRule, PatientProgram
# ==================== MACRO-PROGRESSION APIS ====================

@app.get("/api/programs", tags=["Progression"])
def get_rehab_programs(db: Session = Depends(get_db)):
    """Fetch all available rehab templates for the doctor to assign."""
    programs = db.query(RehabProgram).all()
    return programs

@app.post("/api/patients/{patient_id}/assign-program", tags=["Progression"])
def assign_program(patient_id: int, program_id: int, db: Session = Depends(get_db)):
    """Assign a program to a patient."""
    program = db.query(RehabProgram).filter(RehabProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
        
    first_phase = db.query(ProgramPhase).filter(ProgramPhase.program_id == program_id).order_by(ProgramPhase.phase_order.asc()).first()
    
    patient_prog = PatientProgram(
        patient_id=patient_id,
        program_id=program_id,
        current_phase_id=first_phase.id if first_phase else None
    )
    db.add(patient_prog)
    db.commit()
    return {"status": "success", "message": "Program assigned."}

@app.get("/api/patients/{patient_id}/journey", tags=["Progression"])
def get_patient_journey(patient_id: int, db: Session = Depends(get_db)):
    """Fetch the patient's active program, current phase, and all phases to render the Gamified Map."""
    patient_prog = db.query(PatientProgram).filter(PatientProgram.patient_id == patient_id).first()
    if not patient_prog:
        return {"status": "no_active_program"}
        
    program = db.query(RehabProgram).filter(RehabProgram.id == patient_prog.program_id).first()
    phases = db.query(ProgramPhase).filter(ProgramPhase.program_id == program.id).order_by(ProgramPhase.phase_order.asc()).all()
    
    phases_data = []
    for p in phases:
        exercises = db.query(PhaseExercise).filter(PhaseExercise.phase_id == p.id).all()
        phases_data.append({
            "id": p.id,
            "phase_order": p.phase_order,
            "name": p.name,
            "description": p.description,
            "exercises": [{"type": e.exercise_type, "target_rom": e.target_rom_degrees, "reps": e.reps_per_set} for e in exercises],
            "is_current": p.id == patient_prog.current_phase_id,
            "is_unlocked": p.phase_order <= (patient_prog.current_phase.phase_order if patient_prog.current_phase else 0)
        })
        
    return {
        "program_name": program.name,
        "is_ready_for_next_phase": patient_prog.is_ready_for_next_phase,
        "current_phase_id": patient_prog.current_phase_id,
        "phases": phases_data
    }

@app.post("/api/patients/{patient_id}/approve-promotion", tags=["Progression"])
def approve_promotion(patient_id: int, db: Session = Depends(get_db)):
    """Doctor approves a patient's promotion to the next phase."""
    patient_prog = db.query(PatientProgram).filter(PatientProgram.patient_id == patient_id).first()
    if not patient_prog or not patient_prog.is_ready_for_next_phase:
        raise HTTPException(status_code=400, detail="Patient not ready for promotion.")
        
    current_phase = db.query(ProgramPhase).filter(ProgramPhase.id == patient_prog.current_phase_id).first()
    next_phase = db.query(ProgramPhase).filter(
        ProgramPhase.program_id == patient_prog.program_id,
        ProgramPhase.phase_order > current_phase.phase_order
    ).order_by(ProgramPhase.phase_order.asc()).first()
    
    if next_phase:
        patient_prog.current_phase_id = next_phase.id
        patient_prog.is_ready_for_next_phase = False
        db.commit()
        return {"status": "success", "message": "Patient promoted to next phase."}
    else:
        patient_prog.status = "completed"
        db.commit()
        return {"status": "success", "message": "Program completed!"}
'''

main_path = 'backend/app/main.py'
with open(main_path, 'a') as f:
    f.write(routes_to_append)
print("Routes appended to main.py")