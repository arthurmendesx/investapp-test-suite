"""
test_investments.py

INTEGRANTE 3: POST /api/investments (criação de investimentos válidos)
INTEGRANTE 4: GET /api/investments e DELETE /api/investments/{id}
INTEGRANTE 7: testes DDT via CSV (no final do arquivo)
"""
import csv
from pathlib import Path

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


# ---------------------------------------------------------------------
# INTEGRANTE 4: listagem e exclusao de investimentos
# ---------------------------------------------------------------------
def _criar(base_url, auth_headers, asset="CDB", amount=1500.00):
    response = requests.post(
        f"{base_url}/api/investments",
        json=_payload_valido(asset=asset, amount=amount),
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_listar_investimentos(base_url, auth_headers):
    """GET /api/investments retorna a carteira do usuario (lista)."""
    response = requests.get(
        f"{base_url}/api/investments", headers=auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_listar_contem_investimento_criado(base_url, auth_headers):
    """O investimento recem-criado deve aparecer na listagem."""
    investment_id = _criar(base_url, auth_headers)
    try:
        response = requests.get(
            f"{base_url}/api/investments", headers=auth_headers
        )
        ids = [item["id"] for item in response.json()]
        assert investment_id in ids
    finally:
        _remover(base_url, auth_headers, investment_id)


def test_listar_investimentos_sem_autenticacao(base_url):
    """Sem token a carteira nao pode ser consultada."""
    response = requests.get(f"{base_url}/api/investments")

    assert response.status_code in (401, 403)


def test_excluir_investimento(base_url, auth_headers):
    """DELETE remove o investimento, que some da listagem."""
    investment_id = _criar(base_url, auth_headers)

    response = requests.delete(
        f"{base_url}/api/investments/{investment_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200

    lista = requests.get(
        f"{base_url}/api/investments", headers=auth_headers
    ).json()
    assert investment_id not in [item["id"] for item in lista]


def test_excluir_investimento_inexistente(base_url, auth_headers):
    """Excluir um id que nao existe nao deve retornar sucesso."""
    response = requests.delete(
        f"{base_url}/api/investments/999999999", headers=auth_headers
    )

    assert response.status_code in (404, 400)


# ---------------------------------------------------------------------
# INTEGRANTE 7: testes orientados a dados (DDT) via arquivo CSV
# ---------------------------------------------------------------------
def carregar_dados_investimentos_csv():
    """Le dinamicamente o arquivo tests/data/dados_investimentos.csv."""
    caminho_csv = (
        Path(__file__).resolve().parent.parent
        / "data" / "dados_investimentos.csv"
    )

    if not caminho_csv.exists():
        raise FileNotFoundError(
            f"Arquivo de massa CSV nao encontrado em: {caminho_csv}"
        )

    casos = []
    with open(caminho_csv, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            casos.append(
                (
                    linha["asset_name"],
                    float(linha["amount"]),
                    float(linha["purchase_price"]),
                    int(linha["days_invested"]),
                    int(linha["planned_days"]),
                    int(linha["status_esperado"]),
                )
            )
    return casos


@pytest.mark.parametrize(
    "asset, amount, price, days, planned, status_esperado",
    carregar_dados_investimentos_csv(),
)
def test_criar_investimentos_ddt_csv(
    base_url, auth_headers, asset, amount, price, days, planned,
    status_esperado
):
    """Executa multiplos cenarios de criacao parametrizados via CSV."""
    payload = {
        "asset_name": asset,
        "amount": amount,
        "purchase_price": price,
        "days_invested": days,
        "planned_days": planned,
    }
    response = requests.post(
        f"{base_url}/api/investments", json=payload, headers=auth_headers
    )
    try:
        assert response.status_code == status_esperado, response.text
    finally:
        if response.status_code == 201:
            _remover(base_url, auth_headers, response.json().get("id"))


# ---------------------------------------------------------------------
# INTEGRANTE 8: cenarios negativos e validacao de payload (400/401/422)
# ---------------------------------------------------------------------
def test_criar_investimento_payload_vazio(base_url, auth_headers):
    """Payload sem campos obrigatorios deve retornar 422."""
    response = requests.post(
        f"{base_url}/api/investments", json={}, headers=auth_headers
    )

    assert response.status_code == 422


def test_criar_investimento_tipo_invalido(base_url, auth_headers):
    """amount com texto deve ser rejeitado pela validacao (422)."""
    payload = _payload_valido()
    payload["amount"] = "mil reais"
    response = requests.post(
        f"{base_url}/api/investments", json=payload, headers=auth_headers
    )

    assert response.status_code == 422


def test_criar_investimento_campo_faltando(base_url, auth_headers):
    """Sem planned_days o payload e invalido (422)."""
    payload = _payload_valido()
    del payload["planned_days"]
    response = requests.post(
        f"{base_url}/api/investments", json=payload, headers=auth_headers
    )

    assert response.status_code == 422


def test_token_invalido(base_url):
    """Um token JWT invalido nao deve dar acesso a carteira (401)."""
    headers = {"Authorization": "Bearer token.invalido.qa"}
    response = requests.get(f"{base_url}/api/investments", headers=headers)

    assert response.status_code in (401, 403)


def test_excluir_id_nao_numerico(base_url, auth_headers):
    """id nao numerico na rota de exclusao deve retornar 422."""
    response = requests.delete(
        f"{base_url}/api/investments/abc", headers=auth_headers
    )

    assert response.status_code == 422
