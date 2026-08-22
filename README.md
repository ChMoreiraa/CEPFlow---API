# CEPFlow

API para consulta e validação de endereços brasileiros a partir de um CEP,
usando o [ViaCEP](https://viacep.com.br/) como fonte de dados.

```
Cliente / Postman / Swagger
          │
          ▼
      CEPFlow API
          │
          ▼
       ViaCEP
          │
          ▼
  Processamento/Validação
          │
          ▼
        JSON
```

## Stack

- Python 3.12
- FastAPI + Pydantic
- HTTPX (cliente assíncrono para o ViaCEP)
- Pytest + respx (testes, com o ViaCEP mockado)
- Docker / docker-compose
- Frontend estático (HTML/CSS/JS puro, sem framework)

Sem banco de dados — a API é *stateless*, cada requisição consulta o
ViaCEP na hora.

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger)
em `http://localhost:8000/docs`.

Para abrir a interface, basta abrir `frontend/index.html` no navegador,
ou servir a pasta:

```bash
cd frontend
python -m http.server 8080
```

## Rodando com Docker

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- Interface: `http://localhost:8080`

## Rodando os testes

```bash
pytest -v
```

Os testes mockam as respostas do ViaCEP (com `respx`), então rodam
offline e de forma determinística.

## Endpoints

### `GET /`
Verifica se a API está no ar.

### `GET /api/cep/{cep}`
Consulta um endereço. Aceita CEP com ou sem hífen (`01310100` ou
`01310-100`).

**Sucesso — `200 OK`**
```json
{
  "cep": "01310-100",
  "logradouro": "Avenida Paulista",
  "complemento": "",
  "bairro": "Bela Vista",
  "cidade": "São Paulo",
  "estado": "SP"
}
```

**CEP em formato inválido — `400 Bad Request`**
```json
{ "erro": "cep_invalido", "detalhe": "CEP 'abc' não é válido. Use o formato 12345678 ou 12345-678." }
```

**CEP não encontrado — `404 Not Found`**
```json
{ "erro": "cep_nao_encontrado", "detalhe": "CEP '99999999' não foi encontrado." }
```

**ViaCEP fora do ar — `502 Bad Gateway`**
```json
{ "erro": "servico_indisponivel", "detalhe": "O serviço ViaCEP não respondeu a tempo." }
```

## Estrutura do projeto

```
cepflow/
├── app/
│   ├── main.py         # rotas e tratamento de erros
│   ├── services.py      # integração com o ViaCEP
│   ├── models.py         # schemas Pydantic e validação de CEP
│   └── exceptions.py     # exceções de domínio
├── tests/
│   └── test_api.py
├── frontend/
│   └── index.html
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Próximos passos possíveis

- Cache (Redis) para CEPs consultados com frequência
- Rate limiting
- Persistência opcional de histórico de consultas
- Autenticação por API key para uso em produção
