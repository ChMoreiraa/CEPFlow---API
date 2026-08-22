"""
CEPFlow — API de consulta e validação de endereços a partir de um CEP.

Ponto de entrada da aplicação FastAPI. As rotas ficam bem enxutas por
design: toda a lógica de negócio mora em app/services.py e a validação
de formato em app/models.py.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.exceptions import CepInvalidoError, CepNaoEncontradoError, ServicoIndisponivelError
from app.models import EnderecoResponse, ErrorResponse, cep_e_valido
from app.services import buscar_endereco

app = FastAPI(
    title="CEPFlow",
    description="API de consulta e validação de endereços brasileiros via CEP.",
    version="1.0.0",
    contact={"name": "CEPFlow"},
)

# Libera acesso do front-end local (ou de qualquer origem, para fins de estudo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/", tags=["Status"], summary="Verifica se a API está no ar")
async def raiz():
    return {"status": "online", "servico": "CEPFlow", "docs": "/docs"}


@app.get(
    "/api/cep/{cep}",
    response_model=EnderecoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "CEP em formato inválido"},
        404: {"model": ErrorResponse, "description": "CEP não encontrado"},
        502: {"model": ErrorResponse, "description": "ViaCEP indisponível"},
    },
    tags=["Endereços"],
    summary="Consulta um endereço a partir do CEP",
)
async def consultar_cep(cep: str):
    """
    Recebe um CEP (com ou sem hífen), valida o formato e busca o
    endereço correspondente no ViaCEP.
    """
    if not cep_e_valido(cep):
        raise CepInvalidoError(cep)

    return await buscar_endereco(cep)


# --- Tratamento centralizado de erros ---------------------------------

@app.exception_handler(CepInvalidoError)
async def tratar_cep_invalido(request: Request, exc: CepInvalidoError):
    return JSONResponse(
        status_code=400,
        content={"erro": "cep_invalido", "detalhe": str(exc)},
    )


@app.exception_handler(CepNaoEncontradoError)
async def tratar_cep_nao_encontrado(request: Request, exc: CepNaoEncontradoError):
    return JSONResponse(
        status_code=404,
        content={"erro": "cep_nao_encontrado", "detalhe": str(exc)},
    )


@app.exception_handler(ServicoIndisponivelError)
async def tratar_servico_indisponivel(request: Request, exc: ServicoIndisponivelError):
    return JSONResponse(
        status_code=502,
        content={"erro": "servico_indisponivel", "detalhe": str(exc)},
    )
