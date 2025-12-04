# ============================================================================
# SEED_DATA.PY - SCRIPT PARA POPULAR BANCO COM DADOS DE TESTE
# ============================================================================
# Este script cria dados de exemplo para desenvolvimento e testes:
# - Usuários (psicólogos e pacientes)
# - Pacientes com informações detalhadas
# - Agendamentos com diferentes status
# - Solicitações de agendamento
# - Limpa dados existentes antes de inserir novos
# ============================================================================

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.models import Base, User, Patient, Appointment, Request, UserType, AppointmentStatus, RequestStatus
from Utils import get_password_hash
from datetime import date, timedelta
import json

# Cria todas as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

def seed_database():
    """
    Função principal que popula o banco com dados de teste.
    
    Processo:
        1. Limpa dados existentes
        2. Reseta contadores de ID (SQLite)
        3. Cria usuários (psicólogos e pacientes)
        4. Cria pacientes detalhados
        5. Cria agendamentos de exemplo
        6. Cria solicitações pendentes
    
    Dados criados:
        - 3 psicólogos com especialidades diferentes
        - 1 usuário paciente
        - 4 pacientes detalhados
        - 3 agendamentos (passado, futuro, concluído)
        - 2 solicitações pendentes
    """
    db = SessionLocal()
    try:
        print("🔄 Limpando dados existentes...")
        
        # ====================================================================
        # LIMPEZA DE DADOS EXISTENTES
        # ====================================================================
        
        # Remove todos os dados das tabelas (ordem importante devido às FKs)
        db.query(Request).delete()      # Solicitações
        db.query(Appointment).delete()  # Agendamentos
        db.query(Patient).delete()      # Pacientes
        db.query(User).delete()         # Usuários
        db.commit()

        # Reseta contador de IDs no SQLite (importante para IDs consistentes)
        db.execute("DELETE FROM sqlite_sequence;")
        db.commit()
        
        print("✅ Dados limpos com sucesso!")

        # ====================================================================
        # CRIAÇÃO DE USUÁRIOS (IDs 1-4)
        # ====================================================================
        
        print("👥 Criando usuários...")
        
        users_data = [
            {
                "id": 1,
                "email": "ana@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PSICOLOGO,
                "name": "Dra. Ana Costa",
                "specialty": "Terapia Cognitivo-Comportamental",
                "crp": "CRP 01/23456"
            },
            {
                "id": 2,
                "email": "carlos@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PSICOLOGO,
                "name": "Dr. Carlos Mendes",
                "specialty": "Psicologia Infantil",
                "crp": "CRP 01/34567"
            },
            {
                "id": 3,
                "email": "lucia@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PSICOLOGO,
                "name": "Dra. Lucia Ferreira",
                "specialty": "Terapia Familiar",
                "crp": "CRP 01/45678"
            },
            {
                "id": 4,
                "email": "paciente@test.com",
                "password": get_password_hash("123456"),
                "type": UserType.PACIENTE,
                "name": "Maria Santos"
            }
        ]
        
        # Insere usuários no banco
        for user_data in users_data:
            db.add(User(**user_data))
        db.commit()
        
        print(f"✅ {len(users_data)} usuários criados!")

        # ====================================================================
        # CRIAÇÃO DE PACIENTES DETALHADOS (IDs 5-8)
        # ====================================================================
        
        print("🏥 Criando pacientes...")
        
        patients_data = [
            {
                "id": 5,
                "name": "Fernanda Lima",
                "email": "fernanda.lima@email.com",
                "phone": "(11) 99999-5555",
                "birth_date": date(1992, 3, 12),
                "age": 32,
                "status": "Em tratamento",
                "psychologist_id": 1
            },
            {
                "id": 6,
                "name": "Lucas Pereira",
                "email": "lucas.pereira@email.com",
                "phone": "(11) 99999-6666",
                "birth_date": date(1987, 11, 25),
                "age": 37,
                "status": "Ativo",
                "psychologist_id": 1
            },
            {
                "id": 7,
                "name": "Camila Rodrigues",
                "email": "camila.rodrigues@email.com",
                "phone": "(11) 99999-7777",
                "birth_date": date(1993, 9, 8),
                "age": 31,
                "status": "Em tratamento",
                "psychologist_id": 1
            },
            {
                "id": 8,
                "name": "Maria Santos",
                "email": "paciente@test.com",
                "phone": "(11) 99999-0001",
                "birth_date": date(1990, 5, 15),
                "age": 34,
                "status": "Ativo",
                "psychologist_id": 1
            }
        ]
        
        # Insere pacientes no banco
        for patient_data in patients_data:
            db.add(Patient(**patient_data))
        db.commit()
        
        print(f"✅ {len(patients_data)} pacientes criados!")

        # ====================================================================
        # CRIAÇÃO DE AGENDAMENTOS (IDs 11-13)
        # ====================================================================
        
        print("📅 Criando agendamentos...")
        
        today = date.today()
        appointments_data = [
            {
                "id": 9,
                "patient_id": 8,
                "psychologist_id": 1,
                "date": today - timedelta(days=2),
                "time": "14:00",
                "status": AppointmentStatus.CONCLUIDO,
                "description": "Terapia cognitivo-comportamental",
                "duration": 50,
                "notes": "Sessão produtiva com técnicas de TCC.",
                "full_report": "Paciente respondeu bem às intervenções."
            },
            {
                "id": 10,
                "patient_id": 6,
                "psychologist_id": 1,
                "date": today + timedelta(days=2),
                "time": "15:00",
                "status": AppointmentStatus.AGENDADO,
                "description": "Sessão de acompanhamento",
                "duration": 50,
                "notes": "",
                "full_report": ""
            },
            {
                "id": 11,
                "patient_id": 7,
                "psychologist_id": 1,
                "date": today - timedelta(days=8),
                "time": "11:00",
                "status": AppointmentStatus.CONCLUIDO,
                "description": "Sessão inicial",
                "duration": 60,
                "notes": "Primeira consulta bem-sucedida.",
                "full_report": "Estabelecimento de vínculo terapêutico."
            }
        ]
        
        # Insere agendamentos no banco
        for appointment_data in appointments_data:
            db.add(Appointment(**appointment_data))
        db.commit()
        
        print(f"✅ {len(appointments_data)} agendamentos criados!")

        # ====================================================================
        # CRIAÇÃO DE SOLICITAÇÕES (IDs 14-15)
        # ====================================================================
        
        print("📨 Criando solicitações...")
        
        requests_data = [
            {
                "id": 12,
                "patient_name": "João Silva",
                "patient_email": "joao.silva@email.com",
                "patient_phone": "(11) 99999-1111",
                "preferred_psychologist": 1,
                "description": "Gostaria de agendar uma sessão. Preciso de ajuda com ansiedade e estresse no trabalho.",
                "urgency": "media",
                "preferred_dates": json.dumps(["2024-12-20", "2024-12-21"]),
                "preferred_times": json.dumps(["14:00", "15:00"]),
                "status": RequestStatus.PENDENTE
            },
            {
                "id": 13,
                "patient_name": "Ana Oliveira",
                "patient_email": "ana.oliveira@email.com",
                "patient_phone": "(11) 88888-2222",
                "preferred_psychologist": 2,
                "description": "Gostaria de agendar uma sessão para meu filho de 8 anos.",
                "urgency": "alta",
                "preferred_dates": json.dumps(["2024-12-19"]),
                "preferred_times": json.dumps(["09:00", "10:00"]),
                "status": RequestStatus.PENDENTE
            }
        ]
        
        # Insere solicitações no banco
        for request_data in requests_data:
            db.add(Request(**request_data))
        db.commit()
        
        print(f"✅ {len(requests_data)} solicitações criadas!")
        
        print("\n🎉 DADOS DE TESTE INSERIDOS COM SUCESSO!")
        print("\n📋 RESUMO DOS DADOS CRIADOS:")
        print("   👥 Usuários: 4 (3 psicólogos + 1 paciente)")
        print("   🏥 Pacientes: 4")
        print("   📅 Agendamentos: 3")
        print("   📨 Solicitações: 2")
        print("\n🔑 CREDENCIAIS DE TESTE:")
        print("   ana@test.com / 123456 (Psicóloga)")
        print("   carlos@test.com / 123456 (Psicólogo)")
        print("   lucia@test.com / 123456 (Psicóloga)")
        print("   paciente@test.com / 123456 (Paciente)")

    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        db.rollback()  # Desfaz alterações em caso de erro
    finally:
        db.close()  # Sempre fecha a sessão

# ============================================================================
# EXECUÇÃO DO SCRIPT
# ============================================================================

if __name__ == "__main__":
    """
    Executa o script quando chamado diretamente:
    python seed_data.py
    """
    print("INICIANDO POPULACAO DO BANCO DE DADOS...")
    print("=" * 50)
    seed_database()
    print("=" * 50)
    print("SCRIPT CONCLUIDO!")