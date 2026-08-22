"""
Testes da CEPFlow.

As chamadas ao ViaCEP são mockadas com respx, então os testes rodam
sem depender de internet ou do serviço externo estar no ar.
"""

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.main import app
from app.services import VIACEP_URL

client = TestClient(app)


def test_raiz_confirma_que_api_esta_online():
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "online"


def test_cep_com_formato_invalido_retorna_400():
    resposta = client.get("/api/cep/abc")
    assert resposta.status_code == 400
    assert resposta.json()["erro"] == "cep_invalido"


def test_cep_muito_curto_retorna_400():
    resposta = client.get("/api/cep/123")
    assert resposta.status_code == 400


@respx.mock
def test_cep_valido_retorna_endereco():
    respx.get(VIACEP_URL.format(cep="12345678")).mock(
        return_value=httpx.Response(
            200,
            json={
                "cep": "12345-678",
                "logradouro": "Rua Exemplo",
                "complemento": "",
                "bairro": "Centro",
                "localidade": "São Paulo",
                "uf": "SP",
            },
        )
    )

    resposta = client.get("/api/cep/12345678")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["cep"] == "12345-678"
    assert corpo["cidade"] == "São Paulo"
    assert corpo["estado"] == "SP"


@respx.mock
def test_cep_com_hifen_e_normalizado_antes_da_busca():
    rota = respx.get(VIACEP_URL.format(cep="12345678")).mock(
        return_value=httpx.Response(
            200,
            json={
                "cep": "12345-678",
                "logradouro": "Rua Exemplo",
                "bairro": "Centro",
                "localidade": "São Paulo",
                "uf": "SP",
            },
        )
    )

    resposta = client.get("/api/cep/12345-678")

    assert resposta.status_code == 200
    assert rota.called


@respx.mock
def test_cep_inexistente_retorna_404():
    respx.get(VIACEP_URL.format(cep="99999999")).mock(
        return_value=httpx.Response(200, json={"erro": True})
    )

    resposta = client.get("/api/cep/99999999")

    assert resposta.status_code == 404
    assert resposta.json()["erro"] == "cep_nao_encontrado"


@respx.mock
def test_viacep_fora_do_ar_retorna_502():
    respx.get(VIACEP_URL.format(cep="12345678")).mock(
        side_effect=httpx.ConnectError("conexão recusada")
    )

    resposta = client.get("/api/cep/12345678")

    assert resposta.status_code == 502
    assert resposta.json()["erro"] == "servico_indisponivel"


@respx.mock
def test_viacep_demorando_demais_retorna_502():
    respx.get(VIACEP_URL.format(cep="12345678")).mock(
        side_effect=httpx.TimeoutException("tempo esgotado")
    )

    resposta = client.get("/api/cep/12345678")

    assert resposta.status_code == 502
