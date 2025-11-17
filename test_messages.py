# ============================================================================
# TEST_MESSAGES.PY - TESTE DAS MELHORIAS DO SISTEMA DE MENSAGENS
# ============================================================================
# Script para testar os novos endpoints de mensagens e relacionamentos
# ============================================================================

import requests
import json

BASE_URL = "http://localhost:8000"

def test_message_improvements():
    """Testa as melhorias do sistema de mensagens"""
    
    print("TESTANDO MELHORIAS DO SISTEMA DE MENSAGENS")
    print("=" * 50)
    
    # 1. Login como psicólogo
    print("Fazendo login como psicologo...")
    login_data = {"email": "ana@test.com", "password": "123456"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"Login: {data['user']['name']}")
        else:
            print("Falha no login")
            return
    except:
        print("Servidor nao esta rodando")
        return
    
    # 2. Testar contatos disponíveis
    print("\nTESTANDO CONTATOS DISPONIVEIS")
    try:
        response = requests.get(f"{BASE_URL}/messages/available-contacts", headers=headers)
        if response.status_code == 200:
            contacts = response.json()
            print(f"Contatos encontrados: {len(contacts['contacts'])}")
            for contact in contacts['contacts']:
                print(f"   - {contact['name']} ({contact['type']})")
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 3. Testar pacientes aceitos
    print("\nTESTANDO PACIENTES ACEITOS")
    try:
        response = requests.get(f"{BASE_URL}/patients/my-patients", headers=headers)
        if response.status_code == 200:
            patients = response.json()
            print(f"Pacientes aceitos: {len(patients)}")
            for patient in patients:
                print(f"   - {patient['name']} (ID: {patient['id']})")
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 4. Testar solicitações pendentes
    print("\nTESTANDO SOLICITACOES PENDENTES")
    try:
        response = requests.get(f"{BASE_URL}/requests/", headers=headers)
        if response.status_code == 200:
            requests_data = response.json()
            print(f"Solicitacoes: {len(requests_data)}")
            
            # Se houver solicitações, testar aceitar uma
            if requests_data:
                request_id = requests_data[0]['id']
                print(f"\nTestando aceitar solicitacao ID: {request_id}")
                
                response = requests.patch(
                    f"{BASE_URL}/requests/{request_id}/accept", 
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Paciente aceito: {result['patient_name']}")
                else:
                    print(f"Erro ao aceitar: {response.status_code}")
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 5. Testar iniciar conversa
    print("\nTESTANDO INICIAR CONVERSA")
    try:
        # Tentar iniciar conversa com paciente ID 100
        response = requests.post(
            f"{BASE_URL}/messages/start-conversation",
            params={"receiver_id": 100},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Conversa autorizada: {result['message']}")
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "=" * 50)
    print("TESTES CONCLUIDOS")

if __name__ == "__main__":
    test_message_improvements()