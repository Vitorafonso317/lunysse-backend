from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.models import Base, User, Patient, Appointment, Request, UserType, AppointmentStatus, RequestStatus
from Utils import get_password_hash
from datetime import date, timedelta
import json

Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        print("Limpando dados existentes...")
        
        db.query(Request).delete()
        db.query(Appointment).delete()
        db.query(Patient).delete()
        db.query(User).delete()
        db.commit()

        # Tabelas limpas com sucesso
        
        print("Criando usuarios...")
        
        users_data = [
            {
                "id": 2,
                "email": "ana@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PSICOLOGO,
                "name": "Dra. Ana Costa",
                "specialty": "Terapia Cognitivo-Comportamental",
                "crp": "CRP 01/23456"
            },
            {
                "id": 3,
                "email": "carlos@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PSICOLOGO,
                "name": "Dr. Carlos Mendes",
                "specialty": "Psicologia Infantil",
                "crp": "CRP 01/34567"
            },
            {
                "id": 5,
                "email": "paciente@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PACIENTE,
                "name": "Maria Santos"
            }
        ]
        
        for user_data in users_data:
            db.add(User(**user_data))
        db.commit()
        
        print("Criando pacientes...")
        
        patients_data = [
            {
                "id": 100,
                "name": "Fernanda Lima",
                "email": "fernanda.lima@email.com",
                "phone": "(11) 99999-5555",
                "birth_date": date(1992, 3, 12),
                "age": 32,
                "status": "Em tratamento",
                "psychologist_id": 2
            },
            {
                "id": 101,
                "name": "Lucas Pereira",
                "email": "lucas.pereira@email.com",
                "phone": "(11) 99999-6666",
                "birth_date": date(1987, 11, 25),
                "age": 37,
                "status": "Ativo",
                "psychologist_id": 2
            }
        ]
        
        for patient_data in patients_data:
            db.add(Patient(**patient_data))
        db.commit()
        
        print("Dados inseridos com sucesso!")

    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()