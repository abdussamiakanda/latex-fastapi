from pydantic import BaseModel, field_validator
from typing import Optional
from app.config import AVAILABLE_ENGINES, DEFAULT_ENGINE


class CompileRequest(BaseModel):
    engine: str = DEFAULT_ENGINE
    main: str = "main.tex"
    files: list[dict] = []

    @field_validator("engine")
    @classmethod
    def validate_engine(cls, v: str) -> str:
        if v not in AVAILABLE_ENGINES:
            raise ValueError(
                f"Unsupported engine '{v}'. Available: {', '.join(AVAILABLE_ENGINES)}"
            )
        return v


class CompileResponse(BaseModel):
    success: bool
    pdf: Optional[str] = None
    log: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str


class EnginesResponse(BaseModel):
    default: str
    available: list[str]


class ApiKeyCreate(BaseModel):
    label: str = ""


class ApiKeyResponse(BaseModel):
    id: str
    label: str
    active: bool
    created_at: str


class ApiKeyCreated(BaseModel):
    id: str
    key: str
    label: str
    active: bool
    created_at: str
    message: str = "Save this key — it will not be shown again"


class ApiKeyToggle(BaseModel):
    active: bool

