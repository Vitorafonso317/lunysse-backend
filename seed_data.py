from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.models import Base, User, Patient, Appointment, Request, UserType, AppointmentStatus, RequestStatus
from Utils import get_password_hash
from datetime import date, timedelta
import json

# Cria as tabelas
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        # Limpa dados existentes
        db.query(Request).delete()
        db.query(Appointment).delete()
        db.query(Patient).delete()
        db.query(User).delete()
        db.commit()

        # 🔹 Resetar contador de IDs (importante no SQLite)
        db.execute("DELETE FROM sqlite_sequence;")
        db.commit()

        # ============================================================
        # 🧠 1️⃣ USUÁRIOS (IDs 1–99)
        # ============================================================
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
                "id": 4,
                "email": "lucia@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PSICOLOGO,
                "name": "Dra. Lucia Ferreira",
                "specialty": "Terapia Familiar",
                "crp": "CRP 01/45678"
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

        # ============================================================
        # 🧍‍♀️ 2️⃣ PACIENTES (IDs 100–199)
        # ============================================================
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
            },
            {
                "id": 102,
                "name": "Camila Rodrigues",
                "email": "camila.rodrigues@email.com",
                "phone": "(11) 99999-7777",
                "birth_date": date(1993, 9, 8),
                "age": 31,
                "status": "Em tratamento",
                "psychologist_id": 2
            },
            {
                "id": 103,
                "name": "Maria Santos",
                "email": "paciente@test.com",
                "phone": "(11) 99999-0001",
                "birth_date": date(1990, 5, 15),
                "age": 34,
                "status": "Ativo",
                "psychologist_id": 2
            }
        ]
        for patient_data in patients_data:
            db.add(Patient(**patient_data))
        db.commit()

        # ============================================================
        # 📅 3️⃣ AGENDAMENTOS (IDs 1000–1999)
        # ============================================================
        today = date.today()
        appointments_data = [
            {
                "id": 1000,
                "patient_id": 103,
                "psychologist_id": 2,
                "date": today - timedelta(days=2),
                "time": "14:00",
                "status": AppointmentStatus.CONCLUIDO,
                "description": "Terapia cognitivo-comportamental",
                "duration": 50,
                "notes": "Sessão produtiva com técnicas de TCC.",
                "full_report": "Paciente respondeu bem às intervenções."
            },
            {
                "id": 1001,
                "patient_id": 101,
                "psychologist_id": 2,
                "date": today + timedelta(days=2),
                "time": "15:00",
                "status": AppointmentStatus.AGENDADO,
                "description": "Sessão de acompanhamento",
                "duration": 50,
                "notes": "",
                "full_report": ""
            },
            {
                "id": 1002,
                "patient_id": 102,
                "psychologist_id": 2,
                "date": today - timedelta(days=8),
                "time": "11:00",
                "status": AppointmentStatus.CONCLUIDO,
                "description": "Sessão inicial",
                "duration": 60,
                "notes": "Primeira consulta bem-sucedida.",
                "full_report": "Estabelecimento de vínculo terapêutico."
            }
        ]
        for appointment_data in appointments_data:
            db.add(Appointment(**appointment_data))
        db.commit()

        # ============================================================
        # 📨 4️⃣ SOLICITAÇÕES (IDs 2000–2999)
        # ============================================================
        requests_data = [
            {
                "id": 2000,
                "patient_name": "João Silva",
                "patient_email": "joao.silva@email.com",
                "patient_phone": "(11) 99999-1111",
                "preferred_psychologist": 2,
                "description": "Gostaria de agendar uma sessão. Preciso de ajuda com ansiedade e estresse no trabalho.",
                "urgency": "media",
                "preferred_dates": json.dumps(["2024-12-20", "2024-12-21"]),
                "preferred_times": json.dumps(["14:00", "15:00"]),
                "status": RequestStatus.PENDENTE
            },
            {
                "id": 2001,
                "patient_name": "Ana Oliveira",
                "patient_email": "ana.oliveira@email.com",
                "patient_phone": "(11) 88888-2222",
                "preferred_psychologist": 3,
                "description": "Gostaria de agendar uma sessão para meu filho de 8 anos.",
                "urgency": "alta",
                "preferred_dates": json.dumps(["2024-12-19"]),
                "preferred_times": json.dumps(["09:00", "10:00"]),
                "status": RequestStatus.PENDENTE
            }
        ]
        for request_data in requests_data:
            db.add(Request(**request_data))
        db.commit()

        print("✅ Dados de teste inseridos com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
