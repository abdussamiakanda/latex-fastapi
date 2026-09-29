import json
import uuid
import threading
from datetime import datetime, timezone
from pathlib import Path
from app.config import COMPILER_API_KEYS_FILE


_lock = threading.Lock()


def _read_keys() -> list[dict]:
    path = Path(COMPILER_API_KEYS_FILE)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_keys([])
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_keys(keys: list[dict]) -> None:
    path = Path(COMPILER_API_KEYS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(keys, f, indent=2)


def add_key(label: str = "") -> dict:
    with _lock:
        keys = _read_keys()
        key_value = uuid.uuid4().hex + uuid.uuid4().hex
        entry = {
            "id": uuid.uuid4().hex[:12],
            "key": key_value,
            "label": label,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        keys.append(entry)
        _write_keys(keys)
        return entry


def remove_key(key_id: str) -> bool:
    with _lock:
        keys = _read_keys()
        keys = [k for k in keys if k["id"] != key_id]
        _write_keys(keys)
    return True


def toggle_key(key_id: str, active: bool) -> bool:
    with _lock:
        keys = _read_keys()
        for k in keys:
            if k["id"] == key_id:
                k["active"] = active
                _write_keys(keys)
                return True
    return False


def list_keys() -> list[dict]:
    keys = _read_keys()
    return [
        {"id": k["id"], "label": k["label"], "active": k["active"], "created_at": k["created_at"]}
        for k in keys
    ]


def get_active_keys() -> list[str]:
    keys = _read_keys()
    return [k["key"] for k in keys if k["active"]]


def is_valid_key(api_key: str) -> bool:
    if not api_key:
        return False
    return api_key in get_active_keys()


def find_key(api_key: str) -> dict | None:
    if not api_key:
        return None
    for k in _read_keys():
        if k["key"] == api_key:
            return {"id": k["id"], "label": k["label"], "active": k["active"]}
    return None
