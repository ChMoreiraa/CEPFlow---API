"""
Modelos de dados utilizados pela API.

Aqui ficam os schemas de entrada e saída (Pydantic), responsáveis por
validar e formatar os dados que trafegam pela aplicação.
"""

from pydantic import BaseModel, Field, field_validator


class EnderecoResponse(BaseModel):
    """Representa um endereço já validado e formatado."""

    cep: str = Field(..., examples=["12345-678"])
    logradouro: str = Field(..., examples=["Rua Exemplo"])
    complemento: str = Field(default="", examples=[""])
    bairro: str = Field(..., examples=["Centro"])
    cidade: str = Field(..., examples=["São Paulo"])
    estado: str = Field(..., examples=["SP"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "cep": "12345-678",
                "logradouro": "Rua Exemplo",
                "complemento": "",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
            }
        }
    }


class ErrorResponse(BaseModel):
    """Formato padrão de erro retornado pela API."""

    erro: str
    detalhe: str


def normalizar_cep(cep: str) -> str:
    """Remove qualquer caractere que não seja dígito de um CEP.

    Aceita formatos como '12345-678', '12345 678' ou '12345678'
    e sempre devolve apenas os 8 dígitos.
    """
    return "".join(filter(str.isdigit, cep))


def cep_e_valido(cep: str) -> bool:
    """Verifica se um CEP (já normalizado ou não) tem 8 dígitos numéricos."""
    return len(normalizar_cep(cep)) == 8
