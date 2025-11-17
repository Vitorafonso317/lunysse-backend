# ============================================================================
# MODELS.PY - MODELOS DO BANCO DE DADOS (ORM SQLAlchemy)
# ============================================================================
# Este arquivo define todas as tabelas e relacionamentos do banco de dados:
# - User: Usuários do sistema (psicólogos e pacientes)
# - Patient: Informações detalhadas dos pacientes
# - Appointment: Agendamentos e sessões
# - Request: Solicitações de agendamento
# - Enums: Status e tipos utilizados no sistema
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone
import enum

# ============================================================================
# ENUMS - DEFINIÇÃO DE TIPOS E STATUS
# ============================================================================

class UserType(str, enum.Enum):
    """
    Define os tipos de usuário no sistema.
    
    PSICOLOGO: Profissionais que atendem pacientes
    PACIENTE: Pessoas que recebem atendimento
    """
    PSICOLOGO = "psicologo"
    PACIENTE = "paciente"

class AppointmentStatus(str, enum.Enum):
    """
    Define os possíveis status de um agendamento.
    
    AGENDADO: Sessão marcada, aguardando realização
    CONCLUIDO: Sessão realizada com sucesso
    CANCELADO: Sessão cancelada por algum motivo
    REAGENDADO: Sessão remarcada para outra data/hora
    """
    AGENDADO = "agendado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    REAGENDADO = "reagendado"

class RequestStatus(str, enum.Enum):
    """
    Define os status de uma solicitação de agendamento.
    
    PENDENTE: Aguardando análise do psicólogo
    ACEITO: Solicitação aprovada, agendamento criado
    REJEITADO: Solicitação negada pelo psicólogo
    """
    PENDENTE = "pendente"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"

# ============================================================================
# MODELO USER - USUÁRIOS DO SISTEMA
# ============================================================================

class User(Base):
    """
    Tabela de usuários do sistema (psicólogos e pacientes).
    
    Campos principais:
    - email/password: Credenciais de acesso
    - type: Tipo do usuário (PSICOLOGO ou PACIENTE)
    - name: Nome completo
    - specialty/crp: Específicos para psicólogos
    """
    __tablename__ = "users"
   
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Credenciais de acesso
    email = Column(String, unique=True, index=True)  # Email único para login
    password = Column(String)  # Hash da senha (nunca armazenar senha pura)
    
    # Informações básicas
    type = Column(Enum(UserType))  # PSICOLOGO ou PACIENTE
    name = Column(String)  # Nome completo do usuário
    
    # Campos de perfil
    avatar_url = Column(String, nullable=True)  # URL da foto de perfil
    phone = Column(String, nullable=True)  # Telefone de contato
    birth_date = Column(Date, nullable=True)  # Data de nascimento
    
    # Campos específicos para psicólogos
    specialty = Column(String, nullable=True)  # Especialidade (ex: TCC, Infantil)
    crp = Column(String, nullable=True)  # Registro profissional
    
    # Campos de auditoria
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

# ============================================================================
# MODELO PATIENT - INFORMAÇÕES DETALHADAS DOS PACIENTES
# ============================================================================

class Patient(Base):
    """
    Tabela com informações detalhadas dos pacientes.
    
    Separada da tabela User para permitir:
    - Pacientes sem conta no sistema
    - Informações clínicas específicas
    - Vínculo com psicólogo responsável
    """
    __tablename__ = "patients"
   
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações pessoais
    name = Column(String)  # Nome completo
    email = Column(String)  # Email de contato
    phone = Column(String)  # Telefone
    birth_date = Column(Date)  # Data de nascimento
    age = Column(Integer)  # Idade calculada
    
    # Informações clínicas
    status = Column(String)  # Status do tratamento (Ativo, Em tratamento, etc.)
    emergency_contact = Column(String, nullable=True)  # Contato de emergência
    emergency_phone = Column(String, nullable=True)  # Telefone de emergência
    medical_history = Column(Text, nullable=True)  # Histórico médico
    current_medications = Column(Text, nullable=True)  # Medicações atuais
    
    # Relacionamento com psicólogo
    psychologist_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Metadados
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
   
    # Relacionamentos ORM
    psychologist = relationship("User", foreign_keys=[psychologist_id])
    appointments = relationship("Appointment", back_populates="patient")

# ============================================================================
# MODELO APPOINTMENT - AGENDAMENTOS E SESSÕES
# ============================================================================

class Appointment(Base):
    """
    Tabela de agendamentos e sessões realizadas.
    
    Controla:
    - Data e horário das sessões
    - Status (agendado, concluído, cancelado)
    - Relatórios e anotações da sessão
    """
    __tablename__ = "appointments"
   
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos (quem participa da sessão)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    psychologist_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Informações da sessão
    date = Column(Date, index=True)  # Data da sessão
    time = Column(String)  # Horário (formato: "14:00")
    status = Column(Enum(AppointmentStatus))  # Status atual
    description = Column(String)  # Descrição/tipo da sessão
    duration = Column(Integer, default=50)  # Duração em minutos
    
    # Anotações clínicas
    notes = Column(Text, default="")  # Anotações rápidas
    full_report = Column(Text, default="")  # Relatório completo da sessão
    
    # Metadados
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
   
    # Relacionamentos ORM
    patient = relationship("Patient", back_populates="appointments")
    psychologist = relationship("User")

# ============================================================================
# MODELO REQUEST - SOLICITAÇÕES DE AGENDAMENTO
# ============================================================================

class Request(Base):
    """
    Tabela de solicitações de agendamento.
    
    Permite que:
    - Novos pacientes solicitem atendimento
    - Psicólogos analisem e aprovem solicitações
    - Sistema mantenha histórico de pedidos
    """
    __tablename__ = "requests"
   
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do solicitante
    patient_name = Column(String)  # Nome do paciente
    patient_email = Column(String)  # Email para contato
    patient_phone = Column(String)  # Telefone
    
    # Preferências da solicitação
    preferred_psychologist = Column(Integer, ForeignKey("users.id"))  # Psicólogo desejado
    description = Column(Text)  # Motivo/descrição da solicitação
    urgency = Column(String)  # Nível de urgência (baixa, média, alta)
    
    # Disponibilidade (armazenados como JSON string)
    preferred_dates = Column(Text)  # Datas preferidas ["2024-12-20", "2024-12-21"]
    preferred_times = Column(Text)  # Horários preferidos ["14:00", "15:00"]
    
    # Controle da solicitação
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDENTE)
    notes = Column(Text, default="")  # Anotações do psicólogo
    
    # Metadados
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)  # Última atualização
   
    # Relacionamentos ORM
    psychologist = relationship("User")

# ============================================================================
# MODELO MESSAGE - SISTEMA DE MENSAGENS
# ============================================================================

class Message(Base):
    """
    Tabela de mensagens entre pacientes e psicólogos.
    
    Permite:
    - Comunicação segura entre usuários
    - Controle de leitura das mensagens
    - Histórico completo de conversas
    """
    __tablename__ = "messages"
   
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos (quem envia e recebe)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Conteúdo da mensagem
    content = Column(Text, nullable=False)  # Texto da mensagem
    
    # Controle de leitura
    is_read = Column(Boolean, default=False)  # False = não lida, True = lida
    read_at = Column(DateTime, nullable=True)  # Quando foi lida
    
    # Metadados
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
   
    # Relacionamentos ORM
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])