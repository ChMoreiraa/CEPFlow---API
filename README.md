# CEPFlow

API REST para consulta e validação de endereços brasileiros a partir de um CEP, utilizando o [ViaCEP](https://viacep.com.br/) como fonte de dados.

Projeto construído com foco em código limpo, testável e sem estado — sem banco de dados, sem cache, apenas uma camada fina e bem estruturada sobre o ViaCEP.

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


---

## Índice

- [Stack](#stack)
- [Arquitetura](#arquitetura)
- [Como rodar](#como-rodar)
  - [Local (venv)](#local-venv)
  - [Docker](#docker)
- [Endpoints](#endpoints)
- [Testes](#testes)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Decisões de projeto](#decisões-de-projeto)
- [Limitações conhecidas](#limitações-conhecidas)
- [Roadmap](#roadmap)
- [Licença](#licença)

---

## Stack

| Camada          | Tecnologia                          |
|-----------------|--------------------------------------|
| Linguagem       | Python 3.12                          |
| Framework web   | FastAPI                              |
| Validação       | Pydantic v2                          |
| Cliente HTTP    | HTTPX (assíncrono)                   |
| Testes          | Pytest + respx (mock de HTTP)        |
| Documentação    | Swagger UI / OpenAPI (gerado automaticamente pelo FastAPI) |
| Containerização | Docker + docker-compose              |
| Frontend        | HTML/CSS/JS puro, sem framework      |

Não há banco de dados nem cache: cada requisição consulta o ViaCEP em tempo real. Essa é uma escolha deliberada, não uma limitação — veja [Decisões de projeto](#decisões-de-projeto).

## Arquitetura

O projeto segue uma separação simples de responsabilidades:

app/
├── main.py → rotas HTTP e tratamento de erros (camada de apresentação)
├── services.py → integração com o ViaCEP (camada de acesso a dados externos)
├── models.py → schemas Pydantic e regras de normalização/validação de CEP
└── exceptions.py → exceções de domínio, desacopladas de HTTP


O fluxo de uma requisição:

1. `main.py` recebe `GET /api/cep/{cep}` e valida o formato usando `models.cep_e_valido`.
2. Se válido, delega para `services.buscar_endereco`, que consulta o ViaCEP de forma assíncrona.
3. Erros de domínio (`CepInvalidoError`, `CepNaoEncontradoError`, `ServicoIndisponivelError`) são convertidos em respostas HTTP por `exception_handler`s dedicados — as rotas não têm `try/except` espalhado.
4. A resposta é validada e serializada pelo schema `EnderecoResponse`.

Essa separação existe para que `services.py` possa ser testado, reaproveitado ou trocado (por exemplo, por outro provedor de CEP) sem tocar nas rotas.

## Como rodar

### Local (venv)

Pré-requisitos: Python 3.12+.

```bash
git clone https://github.com/<seu-usuario>/cepflow.git
cd cepflow

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Documentação Swagger: `http://localhost:8000/docs`
- Documentação ReDoc: `http://localhost:8000/redoc`

Para abrir a interface web, sirva a pasta `frontend`:

```bash
cd frontend
python -m http.server 8080
```
Acesse `http://localhost:8080`.

### Docker

Pré-requisitos: Docker e Docker Compose.

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- Interface: `http://localhost:8080`

Para derrubar os containers: `docker compose down`.

## Endpoints

### `GET /`

Verifica se a API está no ar.

```json
{ "status": "online", "servico": "CEPFlow", "docs": "/docs" }
```

### `GET /api/cep/{cep}`

Consulta um endereço a partir de um CEP. Aceita com ou sem hífen (`01310100` ou `01310-100`).

**`200 OK`**
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

**`400 Bad Request`** — CEP em formato inválido (não tem 8 dígitos)
```json
{ "erro": "cep_invalido", "detalhe": "CEP 'abc' não é válido. Use o formato 12345678 ou 12345-678." }
```

**`404 Not Found`** — CEP com formato válido mas inexistente
```json
{ "erro": "cep_nao_encontrado", "detalhe": "CEP '99999999' não foi encontrado." }
```

**`502 Bad Gateway`** — ViaCEP fora do ar, com timeout ou retornando erro
```json
{ "erro": "servico_indisponivel", "detalhe": "O serviço ViaCEP não respondeu a tempo." }
```

### Exemplo com curl

```bash
curl http://localhost:8000/api/cep/01310100
```

## Testes

```bash
pytest -v
```

Todas as chamadas ao ViaCEP são mockadas com `respx`, então os testes rodam offline, de forma determinística e rápida (sem depender do serviço externo estar no ar). A suíte cobre:

- Formato de CEP inválido (`400`)
- CEP válido normalizado com e sem hífen (`200`)
- CEP inexistente (`404`)
- Falha de conexão com o ViaCEP (`502`)
- Timeout do ViaCEP (`502`)

## Estrutura do projeto

cepflow/
├── app/
│ ├── init.py
│ ├── main.py
│ ├── services.py
│ ├── models.py
│ └── exceptions.py
├── tests/
│ ├── init.py
│ └── test_api.py
├── frontend/
│ └── index.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md


## Decisões de projeto

- **Sem banco de dados**: a API é *stateless* por design. Cada CEP é sempre buscado ao vivo no ViaCEP, então não há risco de servir dados desatualizados. O trade-off é latência (uma chamada de rede por requisição) e dependência de disponibilidade do ViaCEP.
- **Erros como exceções de domínio**: `CepInvalidoError`, `CepNaoEncontradoError` e `ServicoIndisponivelError` não conhecem HTTP. A tradução para status code acontece só em `main.py`, via `exception_handler`. Isso mantém `services.py` reutilizável fora de um contexto web (um worker, um CLI, etc.) sem alterações.
- **Testes sem rede real**: usar `respx` para mockar o ViaCEP torna os testes rápidos e confiáveis em CI, sem depender da disponibilidade de um serviço de terceiros.

## Limitações conhecidas

- Sem cache: CEPs consultados com frequência geram uma chamada nova ao ViaCEP a cada vez.
- Sem rate limiting: a API não limita quantidade de requisições por cliente.
- Sem autenticação: todos os endpoints são públicos.
- CORS liberado para todas as origens (`*`) — adequado para desenvolvimento, não recomendado como está para produção.

## Roadmap

- [ ] Cache (Redis ou in-memory com TTL) para CEPs consultados com frequência
- [ ] Rate limiting por IP/API key
- [ ] Autenticação por API key
- [ ] Logging estruturado e métricas (Prometheus)
- [ ] CI com GitHub Actions rodando `pytest` a cada push

## Licença

MIT — sinta-se livre para usar, modificar e distribuir.
