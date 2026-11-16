"""
INTEGRANTE 1 (LIDER): testes de autenticacao em POST /api/login
"""
import os

import requests

TEST_USER = os.getenv("TEST_USER")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")


def test_login_sucesso(base_url):
    """Valida o login com credenciais corretas e o retorno do token JWT."""
    print(f"\n[TEST_AUTH] Testando /api/login para o usuario: '{TEST_USER}'")

    payload = {"username": TEST_USER, "password": TEST_PASSWORD}
    response = requests.post(f"{base_url}/api/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciais_invalidas(base_url):
    """Valida a recusa de autenticacao para senhas incorretas (HTTP 400)."""
    payload = {"username": TEST_USER, "password": "senha_invalida_xyz"}
    response = requests.post(f"{base_url}/api/login", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário ou senha incorretos"


def test_login_usuario_inexistente(base_url):
    """Usuario que nao existe tambem deve ser recusado (HTTP 400)."""
    payload = {"username": "usuario_inexistente_qa", "password": "x"}
    response = requests.post(f"{base_url}/api/login", json=payload)

    assert response.status_code == 400


def test_token_jwt_tem_tres_partes(auth_token):
    """O access_token deve seguir o formato JWT (header.payload.assinatura)."""
    assert isinstance(auth_token, str)
    assert len(auth_token.split(".")) == 3
