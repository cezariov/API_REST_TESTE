# API REST de Gerenciamento de Veiculos

Projeto inicial de uma API REST em Python usando FastAPI para gerenciamento de veiculos.

## Requisitos

- Python 3.11+

## Instalacao

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
pip install -r requirements.txt
```

Opcionalmente, crie um arquivo `.env` a partir do exemplo:

```bash
copy .env.example .env
```

Variaveis principais:

```env
PROJECT_NAME="Vehicle Management API"
DATABASE_URL="sqlite:///./app.db"
JWT_SECRET_KEY="local-development-jwt-secret-key-change-before-production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Por padrao, o projeto usa SQLite local em `app.db`.

## Execucao local

```bash
uvicorn app.main:app --reload
```

A API ficara disponivel em:

```text
http://127.0.0.1:8000
```

## Health check

```http
GET /health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```
