"""
test_simulations.py

INTEGRANTE 5: POST /api/simulate/yield-monthly (rendimento mensal)
INTEGRANTE 6: POST /api/simulate/tax-withdrawal (resgate com otimizacao)
"""
import requests

YIELD_URL = "/api/simulate/yield-monthly"
TAX_URL = "/api/simulate/tax-withdrawal"


# ---------------------------------------------------------------------
# INTEGRANTE 5: simulacao de rendimento mensal
# ---------------------------------------------------------------------
def test_simular_rendimento_padrao(base_url, auth_headers):
    """Sem informar months, usa o padrao (12 meses) e retorna 200."""
    response = requests.post(
        f"{base_url}{YIELD_URL}", json={}, headers=auth_headers
    )

    assert response.status_code == 200, response.text
    print(f"\n[SIM] yield-monthly (padrao): {response.json()}")


def test_simular_rendimento_6_meses(base_url, auth_headers):
    """Simulacao para 6 meses retorna 200 e um JSON valido."""
    response = requests.post(
        f"{base_url}{YIELD_URL}", json={"months": 6}, headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json() is not None


def test_simular_rendimento_months_invalido(base_url, auth_headers):
    """months com texto deve ser rejeitado pela validacao (422)."""
    response = requests.post(
        f"{base_url}{YIELD_URL}",
        json={"months": "doze"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_simular_rendimento_sem_autenticacao(base_url):
    """Sem token a simulacao deve ser negada."""
    response = requests.post(f"{base_url}{YIELD_URL}", json={"months": 12})

    assert response.status_code in (401, 403)


# ---------------------------------------------------------------------
# INTEGRANTE 6: simulacao de resgate com otimizacao fiscal
# ---------------------------------------------------------------------
def test_simular_resgate_valido(base_url, auth_headers):
    """Resgate de um valor alvo retorna 200 e um JSON valido."""
    response = requests.post(
        f"{base_url}{TAX_URL}",
        json={"target_amount": 1000.0},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    print(f"\n[SIM] tax-withdrawal (1000): {response.json()}")


def test_simular_resgate_sem_target(base_url, auth_headers):
    """target_amount e obrigatorio: sem ele a API retorna 422."""
    response = requests.post(
        f"{base_url}{TAX_URL}", json={}, headers=auth_headers
    )

    assert response.status_code == 422


def test_simular_resgate_target_texto(base_url, auth_headers):
    """target_amount com texto deve ser rejeitado (422)."""
    response = requests.post(
        f"{base_url}{TAX_URL}",
        json={"target_amount": "mil"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_simular_resgate_sem_autenticacao(base_url):
    """Sem token a simulacao de resgate deve ser negada."""
    response = requests.post(
        f"{base_url}{TAX_URL}", json={"target_amount": 1000.0}
    )

    assert response.status_code in (401, 403)
