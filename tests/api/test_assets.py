"""
INTEGRANTE 2: GET /api/assets e PUT /api/assets/{asset_id}/rate
"""
import pytest
import requests


def _obter_ativos(base_url):
    response = requests.get(f"{base_url}/api/assets")
    assert response.status_code == 200, response.text
    return response.json()


def test_listar_ativos_publicos(base_url):
    """Consulta pública (sem autenticação) à tabela de taxas de ativos."""
    response = requests.get(f"{base_url}/api/assets")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_listar_ativos_retorna_json(base_url):
    """A resposta deve ter o Content-Type JSON."""
    response = requests.get(f"{base_url}/api/assets")

    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")


def test_ativos_possuem_campos_basicos(base_url):
    """Cada ativo deve ser um objeto JSON não vazio."""
    ativos = _obter_ativos(base_url)

    for ativo in ativos:
        assert isinstance(ativo, dict)
        assert ativo, "Ativo vazio retornado pela API"


# ---------------------------------------------------------------------
# PUT /api/assets/{asset_id}/rate
# ATENÇÃO: confira no Swagger (/docs) o nome do campo do corpo e do
# campo de taxa no retorno. Ajuste apenas as constantes abaixo.
# ---------------------------------------------------------------------
CAMPO_TAXA = "rate"
CAMPO_ID = "id"


def test_atualizar_taxa_ativo_sucesso(base_url, auth_headers):
    """Atualiza a taxa de um ativo e restaura o valor original em seguida."""
    ativos = _obter_ativos(base_url)
    ativo = ativos[0]
    asset_id = ativo.get(CAMPO_ID)
    taxa_original = ativo.get(CAMPO_TAXA)

    if asset_id is None or taxa_original is None:
        pytest.skip(
            f"Ativo sem os campos '{CAMPO_ID}'/'{CAMPO_TAXA}'. "
            "Ajuste as constantes conforme o Swagger."
        )

    nova_taxa = round(float(taxa_original) + 0.01, 4)
    url = f"{base_url}/api/assets/{asset_id}/rate"

    try:
        response = requests.put(
            url, json={CAMPO_TAXA: nova_taxa}, headers=auth_headers
        )
        assert response.status_code == 200, response.text
    finally:
        # Restaura o valor para não alterar a tabela pública do grupo
        requests.put(
            url, json={CAMPO_TAXA: taxa_original}, headers=auth_headers
        )


def test_atualizar_taxa_sem_autenticacao(base_url):
    """Sem token a atualização deve ser negada (401 ou 403)."""
    ativos = _obter_ativos(base_url)
    asset_id = ativos[0].get(CAMPO_ID, 1)

    response = requests.put(
        f"{base_url}/api/assets/{asset_id}/rate", json={CAMPO_TAXA: 1.0}
    )

    assert response.status_code in (401, 403)


def test_atualizar_taxa_ativo_inexistente(base_url, auth_headers):
    """Ativo inexistente não deve retornar sucesso."""
    response = requests.put(
        f"{base_url}/api/assets/99999999/rate",
        json={CAMPO_TAXA: 1.0},
        headers=auth_headers,
    )

    assert response.status_code in (400, 404, 422)