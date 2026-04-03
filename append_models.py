import os

domain_path = 'backend/app/models/domain.py'
schemas_path = 'backend/app/schemas.py'

models_to_append = '''

class RehabProgram(Base):
    __tablename__ = "rehab_programs"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    doctor = relationship("User", foreign_keys=[doctor_id])
    phases = relationship("ProgramPhase", back_populates="program", cascade="all, delete-orphan")

class ProgramPhase(Base):
    __tablename__ = "program_phases"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("rehab_programs.id"))
    phase_order = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    
    program = relationship("RehabProgram", back_populates="phases")
    exercises = relationship("PhaseExercise", back_populates="phase", cascade="all, delete-orphan")
    rules = relationship("PhaseProgressionRule", back_populates="phase", cascade="all, delete-orphan")

class PhaseExercise(Base):
    __tablename__ = "phase_exercises"

    id = Column(Integer, primary_key=True, index=True)
    phase_id = Column(Integer, ForeignKey("program_phases.id"))
    exercise_type = Column(String, nullable=False) 
    target_rom_degrees = Column(Float, nullable=True)
    reps_per_set = Column(Integer, default=10)
    sets_per_day = Column(Integer, default=3)
    
    phase = relationship("ProgramPhase", back_populates="exercises")

class PhaseProgressionRule(Base):
    __tablename__ = "phase_progression_rules"

    id = Column(Integer, primary_key=True, index=True)
    phase_id = Column(Integer, ForeignKey("program_phases.id"))
    metric = Column(String, nullable=False) # 'avg_form_score', 'max_rom'
    operator = Column(String, nullable=False) # '>=', '<='
    target_value = Column(Float, nullable=False)
    sessions_required = Column(Integer, default=3)
    
    phase = relationship("ProgramPhase", back_populates="rules")

class PatientProgram(Base):
    __tablename__ = "patient_programs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    program_id = Column(Integer, ForeignKey("rehab_programs.id"))
    current_phase_id = Column(Integer, ForeignKey("program_phases.id"), nullable=True)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    is_ready_for_next_phase = Column(Boolean, default=False)
    
    patient = relationship("PatientProfile")
    program = relationship("RehabProgram")
    current_phase = relationship("ProgramPhase")
'''

schemas_to_append = '''

# ==================== PROGRAMS ====================
class PhaseExerciseResponse(BaseModel):
    id: int
    exercise_type: str
    target_rom_degrees: Optional[float]
    reps_per_set: int
    sets_per_day: int
    class Config:
        from_attributes = True

class PhaseProgressionRuleResponse(BaseModel):
    id: int
    metric: str
    operator: str
    target_value: float
    sessions_required: int
    class Config:
        from_attributes = True

class ProgramPhaseResponse(BaseModel):
    id: int
    phase_order: int
    name: str
    description: Optional[str]
    exercises: List[PhaseExerciseResponse] = []
    rules: List[PhaseProgressionRuleResponse] = []
    class Config:
        from_attributes = True

class RehabProgramResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    phases: List[ProgramPhaseResponse] = []
    class Config:
        from_attributes = True

class PatientProgramResponse(BaseModel):
    id: int
    program_id: int
    current_phase_id: Optional[int]
    is_ready_for_next_phase: bool
    program: RehabProgramResponse
    current_phase: Optional[ProgramPhaseResponse]
    class Config:
        from_attributes = True
'''

if 'RehabProgram' not in open(domain_path).read():
    with open(domain_path, 'a') as f:
        f.write(models_to_append)
if 'RehabProgramResponse' not in open(schemas_path).read():
    with open(schemas_path, 'a') as f:
        f.write(schemas_to_append)
print('Done appending models and schemas.')