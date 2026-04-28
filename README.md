# Tinnova Veículos API

API REST para gerenciamento de veículos desenvolvida com FastAPI.

O projeto foi estruturado como parte de um desafio técnico, com foco em organização de camadas, autenticação JWT, controle de perfis, persistência com SQLAlchemy, cache de cotação do dólar com Redis e testes automatizados.

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

- Autenticação com JWT
- Perfis `USER` e `ADMIN`
- CRUD de veículos
- Soft delete de veículos
- Filtros por marca, ano, cor e faixa de preço
- Conversão de preço recebido em BRL para USD no cadastro
- Cache Redis para cotação USD/BRL
- Relatório de veículos ativos por marca
- Tratamento global padronizado de erros
- Documentação Swagger/OpenAPI
- Testes automatizados de services, controllers e fluxo de integração

## Como Rodar Localmente

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

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

Documentação Swagger:

```text
http://127.0.0.1:8000/docs
```

Health check:

```http
GET /health
```

## Variáveis de Ambiente

Principais variáveis:

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

Por padrão, o projeto usa SQLite local em `app.db`.

## Redis com Docker

O Redis é usado para cachear a cotação USD/BRL durante o cadastro de veículos.

Suba o Redis com:

```bash
docker compose up -d redis
```

Se o Redis estiver indisponível, a API continua funcionando. Nesse caso, a cotação será buscada diretamente nas APIs externas configuradas.

## Testes

Rodar todos os testes:

```bash
python -m pytest
```

Rodar testes com cobertura:

```bash
python -m pytest --cov=app
```

Os testes usam banco SQLite isolado e não dependem de Redis real nem de APIs externas.

## Autenticação

A API usa JWT Bearer Token.

Perfis:

- `USER`: pode consultar veículos e relatórios.
- `ADMIN`: pode consultar, criar, atualizar e remover veículos.

Para ambiente local/teste, crie um usuário inicial:

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

Autenticação:

- `POST /auth/login`
- `POST /auth/bootstrap`

Veículos:

- `GET /veiculos`
- `GET /veiculos/{id}`
- `POST /veiculos`
- `PUT /veiculos/{id}`
- `PATCH /veiculos/{id}`
- `DELETE /veiculos/{id}`
- `GET /veiculos/relatorios/por-marca`

Utilitário:

- `GET /health`

## Decisões Técnicas

- A aplicação foi organizada em camadas: controllers, services, repositories, schemas, models e database.
- Controllers recebem requisições HTTP e delegam regras para services.
- Services concentram regras de negócio, como validação de placa duplicada, soft delete e conversão BRL para USD.
- Repositories concentram acesso ao banco via SQLAlchemy ORM.
- Veículos usam soft delete com o campo `ativo`, evitando remoção física do banco.
- A cotação USD/BRL usa Redis como cache com TTL configurável.
- Caso Redis falhe, a aplicação segue funcionando e busca a cotação nas APIs externas.
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
- Remover ou proteger melhor o endpoint `/auth/bootstrap` em ambientes não locais.
- Adicionar testes específicos para cache Redis e fallback de cotação.
- Criar pipeline CI para rodar testes e cobertura automaticamente.
- Evoluir logs estruturados e observabilidade.
