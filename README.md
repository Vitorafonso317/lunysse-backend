🧠 LUNYSSE — Sistema de Gestão Psicológica

O Lunysse é uma plataforma moderna e segura para gestão de atendimentos psicológicos, oferecendo recursos completos para psicólogos acompanharem pacientes, agendamentos, relatórios e análises de risco baseadas em Machine Learning.

🧩 Principais Recursos

🔐 Autenticação segura com JWT (login, cadastro, controle de acesso por tipo de usuário)

👥 Gestão de pacientes (criação, listagem, detalhes e vínculo com psicólogos)

🧠 Módulo de psicólogos (listagem e gerenciamento de informações profissionais)

📅 Agendamentos (criação, atualização, cancelamento e histórico de sessões)

📋 Solicitações (pacientes podem solicitar sessões e escolher psicólogos)

📊 Relatórios automatizados (geração de métricas sobre pacientes e sessões)

🤖 Análise de risco com Machine Learning (classificação de pacientes em níveis: baixo, moderado e alto)

🧾 Relatórios integrados com dados do ML, apresentando alertas de risco e taxas de comparecimento

🧱 Estrutura do Projeto
lunysse-backend/
│
├── core/
│   ├── database.py        # Conexão com banco de dados
│   ├── config.py          # Configurações gerais do sistema
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
│   ├── ml_services.py     # Análise de risco via Machine Learning
│
├── routes/
│   ├── auth_routes.py     # Rotas de login e registro
│   ├── patient_routes.py  # Rotas de pacientes
│   ├── psychologist_routes.py # Rotas de psicólogos
│   ├── appointment_routes.py  # Rotas de agendamentos
│   ├── request_routes.py  # Rotas de solicitações
│   ├── report_routes.py   # Rotas de relatórios
│   └── ml_routes.py       # Rotas da análise ML
│
├── main.py                # Ponto de entrada do FastAPI
│
├── requirements.txt       # Dependências do Python
└── README.md              # Este arquivo

⚙️ Tecnologias Utilizadas
🖥️ Backend

FastAPI
 — Framework principal

SQLAlchemy
 — ORM para manipulação do banco

Pydantic
 — Validação de dados

MySQL
 — Banco de dados relacional

JWT (PyJWT)
 — Autenticação segura

[Scikit-learn / Pandas / NumPy] — Suporte à análise de risco e ML

💻 Frontend

React.js
 — Interface moderna e responsiva

Axios
 — Consumo de APIs REST

TailwindCSS
 — Estilização limpa e eficiente

🚀 Como Executar o Projeto
1️⃣ Clone o repositório
git clone https://github.com/seu-usuario/lunysse-backend.git
cd lunysse-backend

2️⃣ Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

3️⃣ Instale as dependências
pip install -r requirements.txt

4️⃣ Configure o banco de dados

No arquivo .env (ou dentro de core/config.py), defina:

DATABASE_URL=mysql+pymysql://usuario:senha@localhost/lunysse_db
SECRET_KEY=sua_chave_jwt_aqui
ALGORITHM=HS256

5️⃣ Rode as migrações (se aplicável)
alembic upgrade head

6️⃣ Inicie o servidor FastAPI
uvicorn main:app --reload


A API estará disponível em:
👉 http://localhost:8000

A documentação automática (Swagger) pode ser acessada em:
👉 http://localhost:8000/docs

🧪 Testes Automatizados

O sistema conta com testes integrados para validação das rotas principais e do módulo de Machine Learning.

Exemplo de execução de testes:

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
✅ Listagem: 1 solicitações

📊 TESTANDO RELATÓRIOS
✅ Relatório gerado com sucesso

🤖 TESTANDO ANÁLISE ML
✅ Análise geral: 3 pacientes analisados
✅ Análise individual: Lucas Pereira — risco baixo

==================================================
✅ TESTES CONCLUÍDOS

🧾 Exemplo de Saída — Relatório
{
  "stats": {
    "active_patients": 4,
    "total_sessions": 3,
    "completed_sessions": 2,
    "canceled_sessions": 0,
    "scheduled_sessions": 1,
    "attendance_rate": "66.7",
    "risk_alerts": []
  },
  "risk_alerts": [
    {
      "id": 2,
      "patient": "Lucas Pereira",
      "risk": "Baixo",
      "reason": "Estabilidade emocional detectada",
      "date": "2025-11-12"
    }
  ]
}
