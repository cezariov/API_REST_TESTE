# Tinnova Veiculos API

API REST para gerenciamento de veiculos desenvolvida com FastAPI.

O projeto foi estruturado como parte de um desafio tecnico, com foco em organizacao de camadas, autenticacao JWT, controle de perfis, persistencia com SQLAlchemy, cache de cotacao do dolar com Redis e testes automatizados.

## Tecnologias

- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic / pydantic-settings
- JWT com python-jose
- Passlib + bcrypt
- Redis
- Pytest
- Pytest-cov

## Funcionalidades

- Autenticacao com JWT
- Perfis `USER` e `ADMIN`
- CRUD de veiculos
- Soft delete de veiculos
- Filtros por marca, ano, cor e faixa de preco
- Conversao de preco recebido em BRL para USD no cadastro
- Cache Redis para cotacao USD/BRL
- Relatorio de veiculos ativos por marca
- Tratamento global padronizado de erros
- Documentacao Swagger/OpenAPI
- Testes automatizados de services, controllers e fluxo de integracao

## Como Rodar Localmente

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Instale as dependencias:

```bash
python -m pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do exemplo:

```bash
copy .env.example .env
```

Execute a API:

```bash
python -m uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000
```

Documentacao Swagger:

```text
http://127.0.0.1:8000/docs
```

Health check:

```http
GET /health
```

## Variaveis de Ambiente

Principais variaveis:

```env
PROJECT_NAME="Vehicle Management API"
DATABASE_URL="sqlite:///./app.db"
JWT_SECRET_KEY="local-development-jwt-secret-key-change-before-production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL="redis://localhost:6379/0"
USD_CACHE_KEY="usd_brl_rate"
USD_CACHE_TTL_SECONDS=3600
```

Por padrao, o projeto usa SQLite local em `app.db`.

## Redis com Docker

O Redis e usado para cachear a cotacao USD/BRL durante o cadastro de veiculos.

Suba o Redis com:

```bash
docker compose up -d redis
```

Se o Redis estiver indisponivel, a API continua funcionando. Nesse caso, a cotacao sera buscada diretamente nas APIs externas configuradas.

## Testes

Rodar todos os testes:

```bash
python -m pytest
```

Rodar testes com cobertura:

```bash
python -m pytest --cov=app
```

Os testes usam banco SQLite isolado e nao dependem de Redis real nem de APIs externas.

## Autenticacao

A API usa JWT Bearer Token.

Perfis:

- `USER`: pode consultar veiculos e relatorios.
- `ADMIN`: pode consultar, criar, atualizar e remover veiculos.

Para ambiente local/teste, crie um usuario inicial:

```http
POST /auth/bootstrap
```

Exemplo:

```json
{
  "email": "admin@example.com",
  "password": "admin123",
  "role": "ADMIN"
}
```

Obtenha o token:

```http
POST /auth/login
```

Exemplo:

```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

Use o token no Swagger clicando em `Authorize` e informando:

```text
Bearer <access_token>
```

## Endpoints Principais

Autenticacao:

- `POST /auth/login`
- `POST /auth/bootstrap`

Veiculos:

- `GET /veiculos`
- `GET /veiculos/{id}`
- `POST /veiculos`
- `PUT /veiculos/{id}`
- `PATCH /veiculos/{id}`
- `DELETE /veiculos/{id}`
- `GET /veiculos/relatorios/por-marca`

Utilitario:

- `GET /health`

## Decisoes Tecnicas

- A aplicacao foi organizada em camadas: controllers, services, repositories, schemas, models e database.
- Controllers recebem requisicoes HTTP e delegam regras para services.
- Services concentram regras de negocio, como validacao de placa duplicada, soft delete e conversao BRL para USD.
- Repositories concentram acesso ao banco via SQLAlchemy ORM.
- Veiculos usam soft delete com o campo `ativo`, evitando remocao fisica do banco.
- A cotacao USD/BRL usa Redis como cache com TTL configuravel.
- Caso Redis falhe, a aplicacao segue funcionando e busca a cotacao nas APIs externas.
- Erros seguem formato padronizado:

```json
{
  "message": "string",
  "code": "string",
  "details": "opcional"
}
```

## Melhorias Futuras

- Configurar migrations com Alembic.
- Remover ou proteger melhor o endpoint `/auth/bootstrap` em ambientes nao locais.
- Adicionar testes especificos para cache Redis e fallback de cotacao.
- Criar pipeline CI para rodar testes e cobertura automaticamente.
- Evoluir logs estruturados e observabilidade.
