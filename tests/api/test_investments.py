"""
test_investments.py

INTEGRANTE 3: POST /api/investments (criação de investimentos válidos)
INTEGRANTE 4: GET /api/investments e DELETE /api/investments/{id}
INTEGRANTE 7: testes DDT via CSV (no final do arquivo)
"""
import pytest
import requests


def _payload_valido(asset="CDB", amount=1000.00):
    return {
        "asset_name": asset,
        "amount": amount,
        "purchase_price": 1.00,
        "days_invested": 30,
        "planned_days": 365,
    }


def _remover(base_url, auth_headers, investment_id):
    """Limpeza: remove o investimento criado pelo teste."""
    if investment_id is not None:
        requests.delete(
            f"{base_url}/api/investments/{investment_id}",
            headers=auth_headers,
        )


# ---------------------------------------------------------------------
# INTEGRANTE 3: criação de investimentos válidos
# ---------------------------------------------------------------------
@pytest.mark.parametrize("asset", ["Poupança", "CDB"])
def test_criar_investimento_valido(base_url, auth_headers, asset):
    """Criação com payload válido deve retornar 201."""
    response = requests.post(
        f"{base_url}/api/investments",
        json=_payload_valido(asset=asset),
        headers=auth_headers,
    )

    try:
        assert response.status_code == 201, response.text
    finally:
        if response.status_code == 201:
            _remover(base_url, auth_headers, response.json().get("id"))


def test_criar_investimento_retorna_id(base_url, auth_headers):
    """O corpo da resposta deve devolver o identificador criado."""
    response = requests.post(
        f"{base_url}/api/investments",
        json=_payload_valido(),
        headers=auth_headers,
    )

    try:
        assert response.status_code == 201, response.text
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("id") is not None
    finally:
        if response.status_code == 201:
            _remover(base_url, auth_headers, response.json().get("id"))


def test_criar_investimento_reflete_dados_enviados(base_url, auth_headers):
    """Os dados enviados devem voltar corretamente na resposta."""
    payload = _payload_valido(asset="CDB", amount=2500.50)
    response = requests.post(
        f"{base_url}/api/investments", json=payload, headers=auth_headers
    )

    try:
        assert response.status_code == 201, response.text
        data = response.json()
        assert data.get("asset_name") == payload["asset_name"]
        assert float(data.get("amount")) == payload["amount"]
    finally:
        if response.status_code == 201:
            _remover(base_url, auth_headers, response.json().get("id"))


def test_criar_investimento_sem_autenticacao(base_url):
    """Sem token, a criação deve ser negada (401 ou 403)."""
    response = requests.post(
        f"{base_url}/api/investments", json=_payload_valido()
    )

    assert response.status_code in (401, 403)
python -m pytest tests/api/test_investments.py -v -s