from core.database import SessionLocal
from models.models import User, UserType
from Utils import get_password_hash

db = SessionLocal()

# Criar usuário paciente
patient_user = User(
    email="maria@test.com",
    password=get_password_hash("123456"),
    name="Maria Santos",
    type=UserType.PACIENTE,
    phone="(11) 99999-1111",
    is_active=True
)

db.add(patient_user)
db.commit()

print("Usuario paciente criado: maria@test.com / 123456")
