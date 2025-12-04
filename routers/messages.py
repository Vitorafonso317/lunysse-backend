from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func
from typing import List
from datetime import datetime

from core.database import get_db
from models.models import Message, User
from services.auth_service import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/")
async def send_message(
    message_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = Message(
        sender_id=current_user.id,
        receiver_id=message_data["receiver_id"],
        content=message_data["content"]
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "content": message.content,
        "is_read": message.is_read,
        "created_at": message.created_at
    }

@router.get("/conversations")
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Buscar todas as mensagens do usuário
    all_messages = db.query(Message).filter(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).order_by(desc(Message.created_at)).all()
    
    # Agrupar por usuário
    user_conversations = {}
    for msg in all_messages:
        other_user_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        
        if other_user_id not in user_conversations:
            other_user = db.query(User).filter(User.id == other_user_id).first()
            
            if not other_user:
                continue
            
            # Contar não lidas
            unread_count = db.query(Message).filter(
                Message.sender_id == other_user_id,
                Message.receiver_id == current_user.id,
                Message.is_read == False
            ).count()
            
            user_conversations[other_user_id] = {
                "user_id": other_user.id,
                "user_name": other_user.name,
                "last_message": msg.content,
                "last_message_at": msg.created_at,
                "unread_count": unread_count
            }
    
    return list(user_conversations.values())

@router.get("/conversation/{user_id}")
async def get_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at).all()
    
    # Marcar como lidas as mensagens recebidas
    db.query(Message).filter(
        Message.sender_id == user_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at
        })
    
    return {"messages": result}

@router.patch("/{message_id}/read")
async def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    db.commit()
    
    return {"success": True}
