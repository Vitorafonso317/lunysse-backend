# ===========================================
# routers/appointments.py
# ===========================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from core.database import get_db
from models.models import Appointment, User, UserType, AppointmentStatus, Patient
from schemas.schemas import AppointmentCreate, AppointmentUpdate, AppointmentSchema
from services.auth_service import get_current_user
from services.email_service import send_email_appointment

router = APIRouter(prefix="/appointments", tags=["appointments"])

# ===========================================
# 1️⃣ Consultar todos os agendamentos do psicólogo autenticado
# ===========================================
@router.get("/", response_model=List[AppointmentSchema])
async def get_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem visualizar seus agendamentos."
        )

    appointments = db.query(Appointment).filter(
        Appointment.psychologist_id == current_user.id
    ).all()

    return appointments


# ===========================================
# 2️⃣ Obter detalhes de um agendamento específico
# ===========================================
@router.get("/{appointment_id}", response_model=AppointmentSchema)
async def get_appointment_by_id(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.psychologist_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )

    return appointment


# ===========================================
# 3️⃣ Criar novo agendamento
# ===========================================
@router.post("/", response_model=AppointmentSchema)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem criar agendamentos."
        )

    # Verifica se o horário já está ocupado
    existing = db.query(Appointment).filter(
        Appointment.psychologist_id == current_user.id,
        Appointment.date == appointment_data.date,
        Appointment.time == appointment_data.time,
        Appointment.status != AppointmentStatus.CANCELADO
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Horário já está agendado."
        )

    appointment = Appointment(
        patient_id=appointment_data.patient_id,
        psychologist_id=current_user.id,
        date=appointment_data.date,
        time=appointment_data.time,
        status=AppointmentStatus.AGENDADO,
        description=appointment_data.description,
        duration=appointment_data.duration,
        notes=appointment_data.notes or "",
        full_report=appointment_data.full_report or ""
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    # Enviar email para o paciente
    try:
        patient = db.query(Patient).filter(Patient.id == appointment_data.patient_id).first()
        if patient and patient.email:
            send_email_appointment(
                client_email=patient.email,
                client_name=patient.name,
                date=str(appointment_data.date),
                time=appointment_data.time
            )
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

    return appointment


# ===========================================
# 4️⃣ Atualizar agendamento existente
# ===========================================
# ===========================================
# 4️⃣ Atualizar agendamento existente
# ===========================================
@router.put("/{appointment_id}", response_model=AppointmentSchema)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.psychologist_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )

    # 1️⃣ Guardar o status anterior
    old_status = appointment.status

    # 2️⃣ Atualizar campos normalmente
    update_fields = appointment_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)

    # 3️⃣ Enviar e-mail apenas se o status mudou
    if "status" in update_fields and old_status != appointment.status:

        # Converter enums para string
        try:
            old_status_str = old_status.value
        except:
            old_status_str = str(old_status)

        try:
            new_status_str = appointment.status.value
        except:
            new_status_str = str(appointment.status)

        # Buscar o paciente no banco
        from models.models import Patient
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()

        if patient:  # evita erro se não existir
            send_email_appointment_status_change(
                patient_email=patient.email,
                patient_name=patient.name,
                old_status=old_status_str,
                new_status=new_status_str,
                appointment_date=str(appointment.date),
                appointment_time=str(appointment.time),
            )

    return appointment




# ===========================================
# 5️⃣ Atualizar agendamento (PATCH)
# ===========================================
@router.patch("/{appointment_id}")
async def patch_appointment(
    appointment_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.psychologist_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    for field, value in update_data.items():
        if hasattr(appointment, field):
            if field == "status":
                setattr(appointment, field, AppointmentStatus(value))
            else:
                setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


# ===========================================
# 6️⃣ Cancelar um agendamento
# ===========================================
@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.psychologist_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )

    appointment.status = AppointmentStatus.CANCELADO
    db.commit()

    # Enviar email de cancelamento
    try:
        from services.email_service import send_email_appointment_status_cancel
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        if patient and patient.email:
            send_email_appointment_status_cancel(
                patient_email=patient.email,
                patient_name=patient.name,
                appointment_date=str(appointment.date),
                appointment_time=appointment.time
            )
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

    return {"message": "Agendamento cancelado com sucesso."}


# ===========================================
# 7️⃣ Buscar agendamentos por email do paciente
# ===========================================
@router.get("/email/{patient_email}")
async def get_appointments_by_email(
    patient_email: str,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.email == patient_email).first()
    
    if not patient:
        return []
    
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.id
    ).all()
    
    return appointments


# ===========================================
# 8️⃣ Listar horários disponíveis
# ===========================================
@router.get("/available-slots")
async def get_available_slots(
    date: str,
    psychologist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_slots = [
        "08:00", "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00", "16:00", "17:00"
    ]
    
    booked = db.query(Appointment).filter(
        Appointment.psychologist_id == psychologist_id,
        Appointment.date == date,
        Appointment.status != AppointmentStatus.CANCELADO
    ).all()
    
    booked_times = [apt.time for apt in booked]
    available = [slot for slot in all_slots if slot not in booked_times]
    
    return {"available_slots": available}


# ===========================================
# 9️⃣ Obter detalhes de uma sessão
# ===========================================
@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == session_id,
        Appointment.psychologist_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    return appointment


# ===========================================
# 🔟 Atualizar status de uma sessão
# ===========================================
@router.patch("/sessions/{session_id}/status")
async def update_session_status(
    session_id: int,
    status_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == session_id,
        Appointment.psychologist_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    new_status = status_data.get("status")
    if new_status:
        appointment.status = AppointmentStatus(new_status)
        db.commit()
    
    return appointment


# ===========================================
# 1️⃣1️⃣ Atualizar notas de uma sessão
# ===========================================
@router.patch("/sessions/{session_id}/notes")
async def update_session_notes(
    session_id: int,
    notes_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == session_id,
        Appointment.psychologist_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    if "notes" in notes_data:
        appointment.notes = notes_data["notes"]
    if "full_report" in notes_data:
        appointment.full_report = notes_data["full_report"]
    
    db.commit()
    db.refresh(appointment)
    
    return appointment
