# ✅ Endpoints Implementados - Lunysse Backend

## 🔐 Autenticação
- ✅ `POST /auth/login` - Login de usuário
- ✅ `POST /auth/register` - Registro de novo usuário

## 👥 Pacientes
- ✅ `GET /patients/` - Listar pacientes do psicólogo logado
- ✅ `POST /patients/` - Criar novo paciente
- ✅ `GET /patients/{id}` - Detalhes de um paciente
- ✅ `GET /patients/{id}/profile` - Perfil completo com estatísticas
- ✅ `GET /patients/{id}/sessions` - Sessões do paciente
- ✅ `POST /patients/{id}/notes` - Adicionar anotação

## 📅 Agendamentos
- ✅ `GET /appointments/` - Listar agendamentos do psicólogo
- ✅ `GET /appointments/{id}` - Detalhes de um agendamento
- ✅ `GET /appointments/email/{email}` - Agendamentos por email do paciente
- ✅ `POST /appointments/` - Criar agendamento
- ✅ `PUT /appointments/{id}` - Atualizar agendamento
- ✅ `DELETE /appointments/{id}` - Cancelar agendamento
- ✅ `GET /appointments/available-slots` - Horários disponíveis

## 🩺 Sessões (Alias para Appointments)
- ✅ `GET /appointments/sessions/{id}` - Detalhes da sessão
- ✅ `PATCH /appointments/sessions/{id}/status` - Atualizar status
- ✅ `PATCH /appointments/sessions/{id}/notes` - Atualizar anotações

## 📋 Solicitações
- ✅ `GET /requests/` - Listar solicitações do psicólogo logado
- ✅ `GET /requests/psychologist/{id}` - Solicitações de um psicólogo
- ✅ `GET /requests/patient/{email}` - Solicitações de um paciente
- ✅ `POST /requests/` - Criar solicitação
- ✅ `PUT /requests/{id}` - Atualizar status da solicitação
- ✅ `PATCH /requests/{id}/read` - Marcar como lida
- ✅ `PATCH /requests/{id}/accept` - Aceitar solicitação

## 📊 Relatórios
- ✅ `GET /reports/{psychologist_id}` - Relatório completo do psicólogo
- ✅ `GET /reports/{psychologist_id}/risk-analysis` - Análise de risco

## 🤖 Machine Learning
- ✅ `GET /ml/risk-analysis` - Análise geral de risco
- ✅ `GET /ml/risk-analysis/{patient_id}` - Análise individual

## 💬 Mensagens
- ✅ `GET /messages/conversations` - Lista de conversas
- ✅ `GET /messages/conversation/{user_id}` - Mensagens de uma conversa
- ✅ `GET /messages/available-contacts` - Contatos disponíveis
- ✅ `POST /messages/` - Enviar mensagem
- ✅ `POST /messages/start-conversation` - Validar início de conversa
- ✅ `GET /messages/unread-count` - Contador de não lidas

## 👨‍⚕️ Psicólogos
- ✅ `GET /psychologists/` - Listar psicólogos
- ✅ `GET /psychologists/{id}` - Detalhes do psicólogo

## 🏥 Sistema
- ✅ `GET /` - Informações da API
- ✅ `GET /health` - Health check
- ✅ `GET /docs` - Documentação Swagger

---

## 📝 Formato de Resposta Padrão

### User
```json
{
  "id": 1,
  "name": "Nome Completo",
  "email": "email@example.com",
  "type": "psicologo",
  "crp": "12345/SP",
  "specialty": "TCC",
  "phone": "(11) 99999-9999",
  "avatar_url": "/avatars/user.jpg",
  "birth_date": "1990-01-01",
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Appointment
```json
{
  "id": 1,
  "patient_id": 1,
  "psychologist_id": 2,
  "date": "2024-01-15",
  "time": "14:00",
  "duration": 50,
  "status": "agendado",
  "description": "Sessão de acompanhamento",
  "notes": "Anotações rápidas",
  "full_report": "Relatório completo",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Request
```json
{
  "id": 1,
  "patient_email": "paciente@example.com",
  "patient_name": "Nome do Paciente",
  "patient_phone": "(11) 99999-9999",
  "psychologist_id": 2,
  "description": "Motivo da solicitação",
  "urgency": "alta",
  "status": "pendente",
  "notes": "Resposta do psicólogo",
  "is_read": false,
  "created_at": "2024-01-15T10:00:00Z",
  "preferred_dates": ["2024-01-20", "2024-01-21"],
  "preferred_times": ["14:00", "15:00"]
}
```

### Message
```json
{
  "id": 1,
  "sender_id": 1,
  "receiver_id": 2,
  "content": "Texto da mensagem",
  "is_read": false,
  "read_at": null,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## 🔒 Autenticação

Todos os endpoints protegidos requerem header:
```
Authorization: Bearer <token_jwt>
```

## 🎯 Status HTTP

- `200` - Sucesso
- `201` - Criado
- `400` - Requisição inválida
- `401` - Não autenticado
- `403` - Sem permissão
- `404` - Não encontrado
- `500` - Erro interno

---

**Total de Endpoints:** 40+
**Status:** ✅ Todos implementados e testados
