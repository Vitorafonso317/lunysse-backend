# 🧠 LUNYSSE — Sistema de Gestão Psicológica

O **Lunysse** é uma plataforma moderna e segura para gestão de atendimentos psicológicos, oferecendo recursos completos para psicólogos acompanharem pacientes, agendamentos, relatórios e análises de risco baseadas em Machine Learning.

## 🧩 Principais Recursos

- 🔐 **Autenticação segura** com JWT (login, cadastro, controle de acesso por tipo de usuário)
- 👥 **Gestão de pacientes** (criação, listagem, detalhes e vínculo com psicólogos)
- 🧠 **Módulo de psicólogos** (listagem e gerenciamento de informações profissionais)
- 📅 **Agendamentos** (criação, atualização, cancelamento e histórico de sessões)
- 📋 **Solicitações** (pacientes podem solicitar sessões e escolher psicólogos)
- 📊 **Relatórios automatizados** (geração de métricas sobre pacientes e sessões)
- 🤖 **Análise de risco com ML** (classificação de pacientes em níveis: baixo, moderado e alto)
- 🧾 **Relatórios integrados** com dados do ML, apresentando alertas de risco e taxas de comparecimento

## 🧱 Estrutura do Projeto

```
lunysse-backend/
│
├── core/
│   └── database.py        # Conexão com banco SQLite
│
├── models/
│   └── models.py          # Definição das tabelas e relacionamentos ORM
│
├── schemas/
│   └── schemas.py         # Validação e serialização de dados com Pydantic
│
├── services/
│   ├── auth_service.py    # Autenticação e controle de usuários
│   ├── report_service.py  # Lógica de geração de relatórios
│   └── ml_services.py     # Análise de risco via Machine Learning
│
├── routers/
│   ├── auth.py            # Rotas de autenticação
│   ├── patients.py        # Rotas de pacientes
│   ├── psychologists.py   # Rotas de psicólogos
│   ├── appointments.py    # Rotas de agendamentos
│   ├── requests.py        # Rotas de solicitações
│   ├── reports.py         # Rotas de relatórios
│   └── ml_analysis.py     # Rotas da análise ML
│
├── main.py                # Ponto de entrada do FastAPI
├── seed_data.py           # Script para popular banco com dados de teste
├── test.py                # Testes automatizados da API
├── Utils.py               # Utilitários (hash de senhas, etc.)
├── lunysse.db             # Banco de dados SQLite
├── .env                   # Variáveis de ambiente
├── requirements.txt       # Dependências do Python
└── README.md              # Este arquivo
```

## ⚙️ Tecnologias Utilizadas

### 🖥️ Backend

- **FastAPI** — Framework web moderno e rápido
- **SQLAlchemy** — ORM para manipulação do banco de dados
- **Pydantic** — Validação e serialização de dados
- **SQLite** — Banco de dados local (arquivo `lunysse.db`)
- **JWT** — Autenticação segura com tokens
- **NumPy** — Computação numérica para análise ML
- **Uvicorn** — Servidor ASGI para FastAPI
- **Passlib** — Hash seguro de senhas
- **Python-Jose** — Manipulação de tokens JWT

### 💻 Frontend (Separado)

- **React.js** — Interface moderna e responsiva
- **Axios** — Consumo de APIs REST
- **TailwindCSS** — Estilização limpa e eficiente

## 🚀 Como Executar o Projeto

### 1️⃣ Clone o repositório
```bash
git clone https://github.com/seu-usuario/lunysse-backend.git
cd lunysse-backend
```

### 2️⃣ Crie e ative o ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instale as dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure as variáveis de ambiente

O arquivo `.env` já está configurado com:
```env
SECRET_KEY=7a19402d6e1a4c0d06859acaa53ccf6fda395ac1e847a390fd063b27be83d3e0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./lunysse.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5️⃣ Popule o banco com dados de teste
```bash
python seed_data.py
```

### 6️⃣ Inicie o servidor FastAPI
```bash
uvicorn main:app --reload
```

### 🌐 Acesso à API

- **API:** http://localhost:8000
- **Documentação (Swagger):** http://localhost:8000/docs
- **Redoc:** http://localhost:8000/redoc

### 👤 Usuários de Teste

| Email | Senha | Tipo | Nome |
|-------|-------|------|----- |
| `ana@test.com` | `123456` | Psicólogo | Dra. Ana Costa |
| `carlos@test.com` | `123456` | Psicólogo | Dr. Carlos Mendes |
| `lucia@test.com` | `123456` | Psicólogo | Dra. Lucia Ferreira |
| `paciente@test.com` | `123456` | Paciente | Maria Santos |

## 🧪 Testes Automatizados

O sistema conta com testes integrados para validação de todas as rotas e funcionalidades.

### Executar testes
```bash
# Certifique-se que o servidor está rodando
uvicorn main:app --reload

# Em outro terminal, execute os testes
python test.py
```

### Exemplo de saída dos testes
```
🧪 INICIANDO TESTES COMPLETOS DO SISTEMA LUNYSSE
==================================================
🔐 Fazendo login...
✅ Login: Dra. Ana Costa

🔑 TESTANDO AUTENTICAÇÃO
Login inválido: ✅
Token válido: ✅

👥 TESTANDO PACIENTES
✅ Listagem: 4 pacientes
Detalhes: ✅

🧠 TESTANDO PSICÓLOGOS
✅ Listagem: 3 psicólogos

📅 TESTANDO AGENDAMENTOS
✅ Listagem: 3 agendamentos

📋 TESTANDO SOLICITAÇÕES
✅ Listagem: 2 solicitações

📊 TESTANDO RELATÓRIOS
✅ Relatório gerado:
   Pacientes ativos: 4
   Total sessões: 3
   Taxa comparecimento: 66.7%

🤖 TESTANDO ANÁLISE ML
✅ Análise geral:
   Total: 4
   Alto risco: 0
   Moderado: 1
   Baixo: 3
✅ Análise individual:
   Fernanda Lima: Baixo
   Score: 0.15

==================================================
✅ TESTES CONCLUÍDOS
```

## 📊 Principais Endpoints da API

### Autenticação
- `POST /auth/login` - Login de usuário
- `POST /auth/register` - Registro de novo usuário

### Pacientes
- `GET /patients/` - Listar pacientes
- `GET /patients/{id}` - Detalhes do paciente
- `POST /patients/` - Criar paciente
- `PUT /patients/{id}` - Atualizar paciente

### Psicólogos
- `GET /psychologists/` - Listar psicólogos
- `GET /psychologists/{id}` - Detalhes do psicólogo

### Agendamentos
- `GET /appointments/` - Listar agendamentos
- `GET /appointments/{id}` - Detalhes do agendamento
- `POST /appointments/` - Criar agendamento
- `PUT /appointments/{id}` - Atualizar agendamento

### Relatórios e ML
- `GET /reports/{psychologist_id}` - Relatório do psicólogo
- `GET /ml/risk-analysis` - Análise geral de risco
- `GET /ml/risk-analysis/{patient_id}` - Análise individual

## 🧾 Exemplo de Resposta — Relatório

```json
{
  "stats": {
    "active_patients": 4,
    "total_sessions": 3,
    "completed_sessions": 2,
    "canceled_sessions": 0,
    "scheduled_sessions": 1,
    "attendance_rate": "66.7"
  },
  "risk_alerts": [
    {
      "id": 101,
      "patient": "Lucas Pereira",
      "risk": "Baixo",
      "reason": "Estabilidade emocional detectada",
      "date": "2024-12-18"
    }
  ]
}
```

## 🔧 Desenvolvimento

### Estrutura de dados
- **Usuários:** Psicólogos e Pacientes com autenticação JWT
- **Pacientes:** Informações pessoais e vínculo com psicólogos
- **Agendamentos:** Sessões com status (agendado, concluído, cancelado)
- **Solicitações:** Pedidos de agendamento de novos pacientes
- **Análise ML:** Classificação de risco baseada em padrões comportamentais

### Banco de dados
O projeto utiliza **SQLite** (`lunysse.db`) para simplicidade no desenvolvimento. Para produção, pode ser facilmente migrado para PostgreSQL ou MySQL alterando apenas a `DATABASE_URL` no arquivo `.env`.

---

**Desenvolvido com ❤️ para facilitar o trabalho de profissionais da psicologia**
