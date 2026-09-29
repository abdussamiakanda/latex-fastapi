import os
from dotenv import load_dotenv

load_dotenv()

COMPILER_API_KEYS_FILE: str = os.getenv("COMPILER_API_KEYS_FILE", "api_keys.json")
COMPILER_TIMEOUT: int = int(os.getenv("COMPILER_TIMEOUT", "60"))
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

LOG_FILE: str = os.getenv("LOG_FILE", "logs/api.log")
LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))
LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

AVAILABLE_ENGINES = ["pdflatex", "xelatex", "lualatex"]
DEFAULT_ENGINE = "pdflatex"

