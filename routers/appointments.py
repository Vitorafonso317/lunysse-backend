# ===========================================
# routers/appointments.py
# ===========================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from core.database import get_db
from models.models import Appointment, User, UserType, AppointmentStatus
from schemas.schemas import AppointmentCreate, AppointmentUpdate, AppointmentSchema
from services.auth_service import get_current_user

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

    return appointment


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

    for field, value in appointment_data.dict(exclude_unset=True).items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)

    return appointment


# ===========================================
# 5️⃣ Cancelar um agendamento
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

    return {"message": "Agendamento cancelado com sucesso."}


# ===========================================
# 6️⃣ Listar horários disponíveis
# ===========================================
@router.get("/available-times")
async def get_available_times(
    date: datetime,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem consultar horários disponíveis."
        )

    start_hour = 8
    end_hour = 18
    slot_duration = timedelta(minutes=50)

    occupied = db.query(Appointment.time).filter(
        Appointment.psychologist_id == current_user.id,
        Appointment.date == date.date(),
        Appointment.status != AppointmentStatus.CANCELADO
    ).all()

    occupied_times = {a.time for a in occupied}
    available = []

    current = datetime.combine(date.date(), datetime.min.time()).replace(hour=start_hour)
    while current.hour < end_hour:
        time_str = current.strftime("%H:%M")
        if time_str not in occupied_times:
            available.append(time_str)
        current += slot_duration

    return {"date": date.date(), "available_times": available}
