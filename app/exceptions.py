"""Exceções específicas do domínio da aplicação."""


class CepInvalidoError(Exception):
    """Lançada quando o CEP informado não tem um formato válido."""

    def __init__(self, cep: str):
        self.cep = cep
        super().__init__(f"CEP '{cep}' não é válido. Use o formato 12345678 ou 12345-678.")


class CepNaoEncontradoError(Exception):
    """Lançada quando o ViaCEP não encontra o CEP consultado."""

    def __init__(self, cep: str):
        self.cep = cep
        super().__init__(f"CEP '{cep}' não foi encontrado.")


class ServicoIndisponivelError(Exception):
    """Lançada quando o ViaCEP está fora do ar ou não responde a tempo."""

    def __init__(self, detalhe: str = "O serviço ViaCEP não respondeu a tempo."):
        self.detalhe = detalhe
        super().__init__(detalhe)
