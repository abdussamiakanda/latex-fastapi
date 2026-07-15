# FastAPI LaTeX Compiler API

Compile LaTeX documents via a REST API using `pdflatex`, `xelatex`, or `lualatex`.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # edit as needed
```

Requires a LaTeX distribution (TeX Live, MiKTeX) installed on the system.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `COMPILER_API_KEY` | *(none)* | API key for request authentication |
| `COMPILER_TIMEOUT` | `60` | Compilation timeout in seconds |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `ENABLE_SHELL_ESCAPE` | `false` | Enable `-shell-escape` flag |

## Run

```bash
uvicorn app.main:app --reload
```

## Endpoints

### `GET /health`
```json
{"status": "ok"}
```

### `GET /engines`
```json
{"default": "pdflatex", "available": ["pdflatex", "xelatex", "lualatex"]}
```

### `POST /compile`

**Modern format:**
```json
{
  "engine": "xelatex",
  "main": "main.tex",
  "files": [
    {"name": "main.tex", "content": "\\documentclass{article}\\n\\begin{document}\\nHello\\n\\end{document}"}
  ]
}
```

**Legacy format (GitLaTeX-compatible):**
```json
{
  "engine": "pdflatex",
  "content": "\\documentclass{article}\\n\\begin{document}\\nHello\\n\\end{document}",
  "bibliography": "",
  "figures": []
}
```

**Response:**
```json
{
  "success": true,
  "pdf": "JVBERi0xLjQK...",
  "log": "This is pdfTeX...",
  "error": null
}
```

**Authentication:** Include `X-API-Key: your_key` or `Authorization: Bearer your_key` header.
