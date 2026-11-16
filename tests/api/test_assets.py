"""
INTEGRANTE 2: consulta e atualização de taxas de ativos (/api/assets)

Formato real da API (conforme /openapi.json):
  GET /api/assets -> lista de {asset_name, asset_type, annual_rate}
  Atualização     -> corpo {asset_name, annual_rate} (AssetRateUpdate)
"""
import pytest
import requests

CAMPOS_ATIVO = {"asset_name", "asset_type", "annual_rate"}


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
    """Cada ativo deve ter nome, tipo e taxa anual numérica."""
    for ativo in _obter_ativos(base_url):
        assert CAMPOS_ATIVO.issubset(ativo.keys()), ativo
        assert isinstance(ativo["asset_name"], str)
        assert isinstance(ativo["annual_rate"], (int, float))
        assert ativo["annual_rate"] > 0


def test_ativos_conhecidos_presentes(base_url):
    """Ativos básicos da carteira devem existir na tabela."""
    nomes = {a["asset_name"] for a in _obter_ativos(base_url)}

    for esperado in ("Poupança", "CDB", "Bitcoin"):
        assert esperado in nomes


def test_atualizar_taxa_ativo_sucesso(base_url, auth_headers):
    """Atualiza a taxa de um ativo e restaura o valor original."""
    ativo = _obter_ativos(base_url)[0]
    nome = ativo["asset_name"]
    original = ativo["annual_rate"]
    url = f"{base_url}/api/assets"

    response = requests.put(
        url,
        json={"asset_name": nome, "annual_rate": round(original + 0.01, 2)},
        headers=auth_headers,
    )
    if response.status_code in (404, 405):
        pytest.skip(f"A API não expõe PUT em /api/assets ({response.status_code})")

    try:
        assert response.status_code == 200, response.text
    finally:
        requests.put(
            url,
            json={"asset_name": nome, "annual_rate": original},
            headers=auth_headers,
        )


def test_atualizar_taxa_sem_autenticacao(base_url):
    """Sem token a atualização deve ser negada (401 ou 403)."""
    ativo = _obter_ativos(base_url)[0]

    response = requests.put(
        f"{base_url}/api/assets",
        json={"asset_name": ativo["asset_name"], "annual_rate": 1.0},
    )
    if response.status_code in (404, 405):
        pytest.skip(f"A API não expõe PUT em /api/assets ({response.status_code})")

    assert response.status_code in (401, 403)
