from core.database import SessionLocal, Base, engine
from models.models import User, Patient, Appointment, Request, UserType, AppointmentStatus, RequestStatus
from Utils import get_password_hash, calculate_age
from datetime import date, datetime, timezone

# Criar tabelas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Limpar dados (se existirem)
try:
    db.query(Request).delete()
    db.query(Appointment).delete()
    db.query(Patient).delete()
    db.query(User).delete()
    db.commit()
except:
    db.rollback()

# Criar psicólogos
psi1 = User(
    email="ana@test.com",
    password=get_password_hash("123456"),
    name="Dra. Ana Costa",
    type=UserType.PSICOLOGO,
    specialty="TCC",
    crp="CRP 06/123456",
    phone="(11) 98765-4321",
    avatar_url="/avatars/ana.jpg",
    is_active=True
)

psi2 = User(
    email="carlos@test.com",
    password=get_password_hash("123456"),
    name="Dr. Carlos Mendes",
    type=UserType.PSICOLOGO,
    specialty="Psicanalise",
    crp="CRP 06/654321",
    phone="(11) 91234-5678",
    is_active=True
)

db.add_all([psi1, psi2])
db.commit()

# Criar pacientes
pac1 = Patient(
    name="Maria Santos",
    email="maria@test.com",
    phone="(11) 99999-1111",
    birth_date=date(1990, 5, 15),
    age=calculate_age(date(1990, 5, 15)),
    status="Ativo",
    psychologist_id=psi1.id,
    emergency_contact="João Santos",
    emergency_phone="(11) 88888-1111",
    medical_history="Sem histórico relevante",
    current_medications="Nenhuma"
)

pac2 = Patient(
    name="João Silva",
    email="joao@test.com",
    phone="(11) 99999-2222",
    birth_date=date(1985, 8, 20),
    age=calculate_age(date(1985, 8, 20)),
    status="Ativo",
    psychologist_id=psi1.id
)

db.add_all([pac1, pac2])
db.commit()

# Criar agendamentos
apt1 = Appointment(
    patient_id=pac1.id,
    psychologist_id=psi1.id,
    date=date(2024, 12, 20),
    time="14:00",
    status=AppointmentStatus.AGENDADO,
    description="Sessao inicial",
    duration=50
)

db.add(apt1)
db.commit()

print("Banco populado com sucesso!")
print(f"Psicologo: ana@test.com / 123456")
print(f"Pacientes: {db.query(Patient).count()}")
