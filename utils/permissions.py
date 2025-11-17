from sqlalchemy.orm import Session
from models.models import Patient, User, Appointment, UserType

def can_access_patient(psychologist_id: int, patient_id: int, db: Session) -> bool:
    """Verifica se psicólogo pode acessar dados do paciente"""
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.psychologist_id == psychologist_id
    ).first()
    return patient is not None

def can_send_message(sender_id: int, receiver_id: int, db: Session) -> bool:
    """Verifica se usuário pode enviar mensagem"""
    sender = db.query(User).filter(User.id == sender_id).first()
    
    if not sender:
        return False
    
    if sender.type == UserType.PSICOLOGO:
        return can_access_patient(sender_id, receiver_id, db)
    else:
        # Paciente pode enviar para seu psicólogo
        patient = db.query(Patient).filter(Patient.id == sender_id).first()
        return patient and patient.psychologist_id == receiver_id
