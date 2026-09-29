import base64
from fastapi import APIRouter, Depends, HTTPException, Request
from app.models import (
    CompileRequest, CompileResponse, HealthResponse, EnginesResponse,
    ApiKeyCreate, ApiKeyResponse, ApiKeyCreated, ApiKeyToggle,
)
from app.config import AVAILABLE_ENGINES, DEFAULT_ENGINE
from app.security import verify_api_key
from app.utils import create_workspace, cleanup_workspace
from app.compiler import process_compile, convert_legacy_request
from app import keys

router = APIRouter()


@router.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/engines")
async def engines() -> EnginesResponse:
    return EnginesResponse(default=DEFAULT_ENGINE, available=AVAILABLE_ENGINES)


@router.post("/compile", response_model=CompileResponse)
async def compile_document(request: Request) -> CompileResponse:
    await verify_api_key(request)

    body = await request.json()

    if "content" in body:
        engine, main, files = convert_legacy_request(body)
    else:
        parsed = CompileRequest(**body)
        engine = parsed.engine
        main = parsed.main
        files = parsed.files

    workspace = create_workspace()
    try:
        pdf_bytes, synctex_bytes = process_compile(engine, main, files, workspace)
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_data_url = f"data:application/pdf;base64,{pdf_b64}"
        synctex_b64 = base64.b64encode(synctex_bytes).decode("utf-8") if synctex_bytes else None
        return CompileResponse(success=True, pdf=pdf_data_url, synctex=synctex_b64)
    except Exception as e:
        return CompileResponse(success=False, error=str(e))
    finally:
        cleanup_workspace(workspace)


@router.get("/keys", response_model=list[ApiKeyResponse])
async def list_keys_route(request: Request) -> list[ApiKeyResponse]:
    await verify_api_key(request)
    return [ApiKeyResponse(**k) for k in keys.list_keys()]


@router.post("/keys", response_model=ApiKeyCreated)
async def create_key(request: Request, body: ApiKeyCreate) -> ApiKeyCreated:
    await verify_api_key(request)
    result = keys.add_key(label=body.label)
    return ApiKeyCreated(**result, message="Save this key — it will not be shown again")


@router.delete("/keys/{key_id}", response_model=dict)
async def delete_key(request: Request, key_id: str) -> dict:
    await verify_api_key(request)
    keys.remove_key(key_id)
    return {"status": "deleted", "id": key_id}


@router.patch("/keys/{key_id}", response_model=ApiKeyResponse)
async def toggle_key(request: Request, key_id: str, body: ApiKeyToggle) -> ApiKeyResponse:
    await verify_api_key(request)
    if not keys.toggle_key(key_id, body.active):
        raise HTTPException(status_code=404, detail="Key not found")
    updated = next((k for k in keys.list_keys() if k["id"] == key_id), None)
    return ApiKeyResponse(**updated)
