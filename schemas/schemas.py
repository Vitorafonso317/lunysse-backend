# ============================================================================
# SCHEMAS.PY - VALIDAÇÃO E SERIALIZAÇÃO DE DADOS (Pydantic)
# ============================================================================
# Este arquivo define os schemas Pydantic para:
# - Validação de dados de entrada (requests)
# - Serialização de dados de saída (responses)
# - Documentação automática da API (Swagger)
# - Conversão entre modelos SQLAlchemy e JSON
# ============================================================================

from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
from models.models import UserType, AppointmentStatus, RequestStatus

# ============================================================================
# USER SCHEMAS - USUÁRIOS DO SISTEMA
# ============================================================================

class UserBase(BaseModel):
    """
    Schema base para usuários - campos comuns a todas as operações.
    Usado como base para outros schemas de usuário.
    """
    email: EmailStr  # Validação automática de formato de email
    name: str
    type: UserType  # PSICOLOGO ou PACIENTE

class UserCreate(UserBase):
    """
    Schema para criação de novos usuários.
    Inclui senha e campos opcionais específicos para psicólogos.
    """
    password: str  # Senha em texto puro (será hasheada)
    specialty: Optional[str] = None  # Especialidade (apenas psicólogos)
    crp: Optional[str] = None  # Registro profissional (apenas psicólogos)
    phone: Optional[str] = None  # Telefone de contato
    birth_date: Optional[date] = None  # Data de nascimento (obrigatória apenas para pacientes)

class UserLogin(BaseModel):
    """
    Schema para login de usuários.
    Apenas email e senha são necessários.
    """
    email: str
    password: str

class User(UserBase):
    """
    Schema de resposta para usuários.
    Retorna dados do usuário sem a senha.
    """
    id: int
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None
    specialty: Optional[str] = None
    crp: Optional[str] = None
    phone: Optional[str] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True  # Permite conversão de modelos SQLAlchemy

class Token(BaseModel):
    """
    Schema de resposta para autenticação.
    Retorna token JWT e dados do usuário.
    """
    access_token: str  # Token JWT
    token_type: str  # Tipo do token (sempre "bearer")
    user: User  # Dados do usuário logado

# ============================================================================
# PATIENT SCHEMAS - PACIENTES
# ============================================================================

class PatientBase(BaseModel):
    """
    Schema base para pacientes - informações pessoais básicas.
    """
    name: str
    email: EmailStr
    phone: str
    birth_date: date

class PatientCreate(PatientBase):
    """
    Schema para criação de novos pacientes.
    Inclui ID do psicólogo responsável.
    """
    psychologist_id: int  # ID do psicólogo que atenderá o paciente

class Patient(PatientBase):
    """
    Schema de resposta para pacientes.
    Inclui dados calculados e metadados.
    """
    id: int
    age: int  # Idade calculada automaticamente
    status: str  # Status do tratamento
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    psychologist_id: Optional[int] = None
    total_session: Optional[int] = 0  # Total de sessões realizadas
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# APPOINTMENT SCHEMAS - AGENDAMENTOS
# ============================================================================

class AppointmentBase(BaseModel):
    """
    Schema base para agendamentos - informações essenciais da sessão.
    """
    patient_id: int
    date: date  # Data da sessão
    time: str  # Horário (formato: "14:00")
    description: str  # Tipo/descrição da sessão
    duration: Optional[int] = 50  # Duração em minutos (padrão: 50min)
    notes: Optional[str] = None  # Anotações rápidas
    full_report: Optional[str] = None  # Relatório completo

class AppointmentCreate(AppointmentBase):
    """
    Schema para criação de agendamentos.
    Psicólogo é inferido do usuário logado.
    """
    pass

class AppointmentUpdate(BaseModel):
    """
    Schema para atualização de agendamentos.
    Todos os campos são opcionais para updates parciais.
    """
    date: Optional[date] = None
    time: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    notes: Optional[str] = None
    full_report: Optional[str] = None

class AppointmentSchema(AppointmentBase):
    """
    Schema de resposta para agendamentos.
    Inclui ID, status e metadados.
    """
    id: int
    psychologist_id: int
    status: AppointmentStatus  # AGENDADO, CONCLUIDO, CANCELADO, REAGENDADO
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# REQUEST SCHEMAS - SOLICITAÇÕES DE AGENDAMENTO
# ============================================================================

class RequestBase(BaseModel):
    """
    Schema base para solicitações de agendamento.
    Informações fornecidas pelo paciente interessado.
    """
    patient_name: str
    patient_email: EmailStr
    patient_phone: str
    preferred_psychologist: int  # ID do psicólogo desejado
    description: str  # Motivo da solicitação
    urgency: Optional[str] = "media"  # Nível de urgência (baixa, média, alta)
    preferred_dates: Optional[List[str]] = []  # Datas preferidas ["2024-12-20", "2024-12-21"]
    preferred_times: Optional[List[str]] = []  # Horários preferidos ["14:00", "15:00"]

class RequestCreate(RequestBase):
    """
    Schema para criação de solicitações.
    Idêntico ao base - todas as informações são obrigatórias.
    """
    pass

class RequestUpdate(BaseModel):
    """
    Schema para atualização de solicitações pelo psicólogo.
    Permite aprovar/rejeitar e adicionar notas.
    """
    status: RequestStatus  # PENDENTE, ACEITO, REJEITADO
    notes: Optional[str] = None  # Observações do psicólogo

class Request(RequestBase):
    """
    Schema de resposta para solicitações.
    Inclui status, notas e timestamps.
    """
    id: int
    status: RequestStatus
    notes: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============================================================================
# PSYCHOLOGIST SCHEMAS - PSICÓLOGOS (VISÃO SIMPLIFICADA)
# ============================================================================

class Psychologist(BaseModel):
    """
    Schema simplificado para listagem de psicólogos.
    Usado em endpoints públicos e seleção de profissionais.
    """
    id: int
    name: str
    specialty: str  # Especialidade profissional
    crp: str  # Registro no Conselho Regional de Psicologia

    class Config:
        from_attributes = True

# ============================================================================
# REPORTS & ANALYTICS SCHEMAS - RELATÓRIOS E ANÁLISES
# ============================================================================

class ReportStats(BaseModel):
    """
    Schema para estatísticas gerais do psicólogo.
    Usado em dashboards e relatórios.
    """
    active_patients: int  # Pacientes ativos
    total_sessions: int  # Total de sessões
    completed_sessions: int  # Sessões concluídas
    canceled_sessions: int  # Sessões canceladas
    scheduled_sessions: int  # Sessões agendadas
    attendance_rate: str  # Taxa de comparecimento (%)
    risk_alerts: List[dict]  # Alertas de risco dos pacientes

class FrequencyData(BaseModel):
    """
    Schema para dados de frequência temporal.
    Usado em gráficos de sessões por mês.
    """
    month: str  # Nome do mês
    sessions: int  # Quantidade de sessões

class StatusData(BaseModel):
    """
    Schema para dados de status com cores.
    Usado em gráficos de pizza/donut.
    """
    name: str  # Nome do status
    value: int  # Quantidade
    color: str  # Cor para o gráfico

class RiskAlert(BaseModel):
    """
    Schema para alertas de risco de pacientes.
    Gerado pela análise de Machine Learning.
    """
    id: int  # ID do paciente
    patient: str  # Nome do paciente
    risk: str  # Nível de risco (Baixo, Moderado, Alto)
    reason: str  # Motivo do alerta
    date: str  # Data da análise

class ReportsData(BaseModel):
    """
    Schema principal para relatórios completos.
    Combina estatísticas e alertas de risco.
    """
    stats: ReportStats  # Estatísticas gerais
    risk_alerts: List[RiskAlert]  # Lista de alertas de risco

# =========================================================
# MESSAGE SCHEMAS
# =========================================================
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int

class MessageSchema(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationSchema(BaseModel):
    user_id: int
    user_name: str
    last_message: str
    last_message_at: datetime
    unread_count: int

class UnreadCountSchema(BaseModel):
    unread_count: int