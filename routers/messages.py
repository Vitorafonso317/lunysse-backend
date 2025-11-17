from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime, timezone
from core.database import get_db
from models.models import Message, User, Patient, UserType, Appointment
from schemas.schemas import MessageCreate, MessageSchema, UnreadCountSchema
from services.auth_service import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=MessageSchema)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar nova mensagem com validação de relacionamento"""
    receiver_id = message_data.receiver_id
    
    # VALIDAÇÃO DE RELACIONAMENTO
    if current_user.type == UserType.PSICOLOGO:
        patient = db.query(Patient).filter(
            Patient.id == receiver_id,
            Patient.psychologist_id == current_user.id
        ).first()
        if not patient:
            raise HTTPException(status_code=403, detail="Você só pode enviar mensagens para seus pacientes")
    
    elif current_user.type == UserType.PACIENTE:
        appointment = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id,
            Appointment.psychologist_id == receiver_id
        ).first()
        if not appointment:
            raise HTTPException(status_code=403, detail="Você só pode enviar mensagens para seus psicólogos")
    
    # Criar mensagem
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=message_data.content,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message

@router.get("/conversation/{user_id}")
async def get_conversation(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca conversa com validação de relacionamento"""
    
    # VALIDAR RELACIONAMENTO
    has_relationship = False
    
    if current_user.type == UserType.PSICOLOGO:
        patient = db.query(Patient).filter(
            Patient.id == user_id,
            Patient.psychologist_id == current_user.id
        ).first()
        has_relationship = patient is not None
    
    elif current_user.type == UserType.PACIENTE:
        appointment = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id,
            Appointment.psychologist_id == user_id
        ).first()
        has_relationship = appointment is not None
    
    if not has_relationship:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar esta conversa")
    
    # Buscar mensagens
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at).all()
    
    return {"messages": messages, "total": len(messages)}

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas as conversas do usuário"""
    
    # Buscar mensagens do usuário
    messages = db.query(Message).filter(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).order_by(desc(Message.created_at)).all()
    
    # Extrair IDs únicos
    user_ids = set()
    for msg in messages:
        other_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        user_ids.add(other_id)
    
    conversations = []
    for user_id in user_ids:
        # Última mensagem
        last_msg = db.query(Message).filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
            )
        ).order_by(desc(Message.created_at)).first()
        
        if last_msg:
            # Não lidas
            unread = db.query(Message).filter(
                Message.sender_id == user_id,
                Message.receiver_id == current_user.id,
                Message.is_read == False
            ).count()
            
            # Nome do usuário
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                patient = db.query(Patient).filter(Patient.id == user_id).first()
                user_name = patient.name if patient else f"Usuario {user_id}"
            else:
                user_name = user.name
            
            conversations.append({
                "user_id": user_id,
                "user_name": user_name,
                "last_message": last_msg.content,
                "last_message_at": last_msg.created_at,
                "unread_count": unread
            })
    
    return conversations

@router.get("/available-contacts")
async def get_available_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista contatos disponíveis para mensagem"""
    
    contacts = []
    
    if current_user.type == UserType.PSICOLOGO:
        patients = db.query(Patient).filter(
            Patient.psychologist_id == current_user.id
        ).all()
        
        for patient in patients:
            contacts.append({
                "id": patient.id,
                "name": patient.name,
                "email": patient.email,
                "type": "patient"
            })
    
    elif current_user.type == UserType.PACIENTE:
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id
        ).all()
        
        psychologist_ids = list(set([a.psychologist_id for a in appointments]))
        
        for psych_id in psychologist_ids:
            psychologist = db.query(User).filter(User.id == psych_id).first()
            if psychologist:
                contacts.append({
                    "id": psychologist.id,
                    "name": psychologist.name,
                    "email": psychologist.email,
                    "type": "psychologist"
                })
    
    return {"contacts": contacts}

@router.post("/start-conversation")
async def start_conversation(
    receiver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Valida se pode iniciar conversa"""
    
    has_relationship = False
    
    if current_user.type == UserType.PSICOLOGO:
        patient = db.query(Patient).filter(
            Patient.id == receiver_id,
            Patient.psychologist_id == current_user.id
        ).first()
        has_relationship = patient is not None
    
    elif current_user.type == UserType.PACIENTE:
        appointment = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id,
            Appointment.psychologist_id == receiver_id
        ).first()
        has_relationship = appointment is not None
    
    if not has_relationship:
        raise HTTPException(status_code=403, detail="Sem relacionamento ativo")
    
    return {"can_message": True, "receiver_id": receiver_id, "message": "Conversa autorizada"}

@router.get("/unread-count", response_model=UnreadCountSchema)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Contar mensagens não lidas"""
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return {"unread_count": count}