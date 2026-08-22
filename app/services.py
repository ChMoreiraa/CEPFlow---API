"""
Camada responsável por conversar com o ViaCEP e traduzir a resposta
para o formato usado pela CEPFlow.
"""

import httpx

from app.exceptions import CepNaoEncontradoError, ServicoIndisponivelError
from app.models import EnderecoResponse, normalizar_cep

VIACEP_URL = "https://viacep.com.br/ws/{cep}/json/"
TIMEOUT_SEGUNDOS = 5.0


async def buscar_endereco(cep: str) -> EnderecoResponse:
    """Consulta o ViaCEP e devolve o endereço já normalizado.

    Levanta CepNaoEncontradoError se o CEP não existir, ou
    ServicoIndisponivelError se o ViaCEP não puder ser contatado.
    """
    cep_numerico = normalizar_cep(cep)
    url = VIACEP_URL.format(cep=cep_numerico)

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS) as client:
            resposta = await client.get(url)
    except httpx.TimeoutException as exc:
        raise ServicoIndisponivelError("Tempo esgotado ao consultar o ViaCEP.") from exc
    except httpx.RequestError as exc:
        raise ServicoIndisponivelError(f"Falha de conexão com o ViaCEP: {exc}") from exc

    if resposta.status_code != 200:
        raise ServicoIndisponivelError(
            f"ViaCEP retornou status inesperado: {resposta.status_code}"
        )

    dados = resposta.json()

    # O ViaCEP responde com {"erro": true} quando o CEP não existe
    if dados.get("erro"):
        raise CepNaoEncontradoError(cep_numerico)

    return _mapear_resposta(dados)


def _mapear_resposta(dados: dict) -> EnderecoResponse:
    """Converte o payload do ViaCEP para o schema da CEPFlow."""
    return EnderecoResponse(
        cep=dados.get("cep", ""),
        logradouro=dados.get("logradouro", ""),
        complemento=dados.get("complemento", ""),
        bairro=dados.get("bairro", ""),
        cidade=dados.get("localidade", ""),
        estado=dados.get("uf", ""),
    )
