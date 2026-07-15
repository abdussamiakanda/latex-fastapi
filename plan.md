# FastAPI LaTeX Compiler API - Project Plan

## Goal

Build a production-ready FastAPI service to replace the existing Flask compiler while remaining backward compatible with the current frontend.

## Core Features

- FastAPI + Uvicorn
- GitLaTeX-compatible `/compile`
- Legacy request compatibility
- Engine selection:
  - `pdflatex` (default)
  - `xelatex`
  - `lualatex`
- API key protection (no user authentication, accounts, or JWT)
- CORS support
- Temporary isolated workspaces
- Secure path validation
- Base64 PDF response
- Health endpoint
- Engine discovery endpoint

---

# Project Structure

```text
latex-api/
ÃÄÄ app/
³   ÃÄÄ main.py
³   ÃÄÄ config.py
³   ÃÄÄ models.py
³   ÃÄÄ compiler.py
³   ÃÄÄ security.py
³   ÃÄÄ utils.py
³   ÀÄÄ routes.py
ÃÄÄ requirements.txt
ÃÄÄ .env.example
ÃÄÄ README.md
ÀÄÄ plan.md
```

---

# API Security

There is **no user authentication**.

Every request to `/compile` must include the configured API key.

Supported headers:

```
X-API-Key: your_api_key
```

or

```
Authorization: Bearer your_api_key
```

Environment variable:

```
COMPILER_API_KEY=your_secret_key
```

---

# Endpoints

## GET /health

Returns:

```json
{
  "status":"ok"
}
```

## GET /engines

Returns:

```json
{
  "default":"pdflatex",
  "available":[
    "pdflatex",
    "xelatex",
    "lualatex"
  ]
}
```

## POST /compile

Modern format:

```json
{
  "engine":"xelatex",
  "main":"main.tex",
  "files":[]
}
```

Legacy format:

```json
{
  "content":"...",
  "bibliography":"...",
  "figures":[]
}
```

If `engine` is omitted, use `pdflatex`.

---

# Compilation Flow

1. Validate API key (if configured).
2. Validate request body.
3. Create temporary workspace.
4. Save uploaded files.
5. Detect bibliography.
6. Select LaTeX engine.
7. Compile.
8. Read PDF.
9. Encode PDF as Base64.
10. Return JSON.
11. Remove temporary directory.

---

# Configuration

- COMPILER_API_KEY
- COMPILER_TIMEOUT
- HOST
- PORT
- ENABLE_SHELL_ESCAPE

---

# Future

- Tectonic support
- Docker sandbox
- Rate limiting
- Structured logging
- Metrics

