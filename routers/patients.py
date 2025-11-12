# Importações necessárias
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.models import Patient, User, Appointment, UserType
from schemas.schemas import PatientCreate, Patient as PatientSchema
from services.auth_service import get_current_user
from Utils import calculate_age

# Criação do roteador FastAPI para a entidade "patients"
router = APIRouter(prefix="/patients", tags=["patients"])

# ======================================
# Rota para listar pacientes do psicólogo
# ======================================
@router.get("/", response_model=List[PatientSchema])
async def get_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem acessar lista de pacientes"
        )
    
    patients = db.query(Patient).filter(
        Patient.psychologist_id == current_user.id
    ).all()
    
    # Calcula o total de sessões para cada paciente e mantém o nome do campo do schema (total_session)
    for patient in patients:
        total_sessions = db.query(Appointment).filter(
            Appointment.patient_id == patient.id,
            Appointment.psychologist_id == current_user.id
        ).count()
        # Usa o mesmo nome de campo definido no schema: total_session
        patient.total_session = total_sessions
    
    return patients

# ======================================
# Rota para obter detalhes de um paciente específico
# ======================================
@router.get("/{patient_id}", response_model=PatientSchema)
async def get_patient_detail(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Apenas psicólogos podem acessar detalhes dos pacientes
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem acessar detalhes de pacientes"
        )

    # Busca o paciente específico que pertence ao psicólogo logado
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.psychologist_id == current_user.id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )

    # Conta o total de sessões do paciente (mantendo o nome do campo conforme schema)
    total_sessions = db.query(Appointment).filter(
        Appointment.patient_id == patient.id,
        Appointment.psychologist_id == current_user.id
    ).count()

    patient.total_session = total_sessions

    return patient

# ======================================
# Rota para criar um novo paciente
# ======================================
@router.post("/", response_model=PatientSchema)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem cadastrar pacientes"
        )
    
    existing_patient = db.query(Patient).filter(
        Patient.email == patient_data.email,
        Patient.psychologist_id == patient_data.psychologist_id
    ).first()
    
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paciente com este email já está cadastrado"
        )
    
    age = calculate_age(patient_data.birth_date)
    
    db_patient = Patient(
        name=patient_data.name,
        email=patient_data.email,
        phone=patient_data.phone,
        birth_date=patient_data.birth_date,
        age=age,
        status="Ativo",
        psychologist_id=patient_data.psychologist_id
    )
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient

# ======================================
# Rota para listar sessões de um paciente
# ======================================
@router.get("/{patient_id}/sessions")
async def get_patient_sessions(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem acessar sessões de pacientes"
        )
    
    sessions = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.psychologist_id == current_user.id
    ).all()
    
    return sessions

# ======================================
# Rota para adicionar uma anotação a um paciente
# ======================================
@router.post("/{patient_id}/notes")
async def add_patient_note(
    patient_id: int,
    note_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem adicionar anotações"
        )
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.psychologist_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # TODO: Implementar sistema de anotações separadamente no banco
    return {"id": patient_id, "message": "Anotação adicionada com sucesso"}
