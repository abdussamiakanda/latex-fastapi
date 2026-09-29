import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import HOST, PORT
from app.logging_setup import log_call
from app.routes import router

app = FastAPI(
    title="LaTeX Compiler API",
    description="FastAPI service for compiling LaTeX documents with pdflatex, xelatex, or lualatex.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started = time.perf_counter()
    status_code = 500
    error = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        raise
    finally:
        entry = {
            "ip": _client_ip(request),
            "method": request.method,
            "path": request.url.path,
            "query": request.url.query,
            "status": status_code,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            "key_id": getattr(request.state, "key_id", None),
            "key_label": getattr(request.state, "key_label", None),
            "user_agent": request.headers.get("User-Agent", ""),
        }
        detail = getattr(request.state, "log_detail", None)
        if detail:
            entry.update(detail)
        if error:
            entry["error"] = error
        log_call(entry)


app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)

