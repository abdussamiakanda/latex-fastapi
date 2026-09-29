import base64 as b64
import subprocess
import shutil
from pathlib import Path
from app.config import COMPILER_TIMEOUT
from app.utils import resolve_file_path, detect_main_tex


def _find_engine(engine: str) -> str:
    path = shutil.which(engine)
    if path is None:
        raise RuntimeError(f"LaTeX engine '{engine}' not found on system PATH")
    return path


def _run_latex_pass(engine_path: str, main_tex: str, workdir: Path, stem: str) -> None:
    cmd = [
        engine_path,
        "-shell-escape",
        "-interaction=nonstopmode",
        "-file-line-error",
        "-synctex=1",
        main_tex,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=COMPILER_TIMEOUT,
        cwd=str(workdir),
    )
    if result.returncode != 0:
        log_file = workdir / f"{stem}.log"
        log_content = ""
        if log_file.exists():
            log_content = log_file.read_text(encoding="utf-8", errors="ignore")
        err_text = result.stderr or result.stdout or log_content or "LaTeX pass failed"
        raise RuntimeError(err_text)


def compile_latex(engine: str, main_tex: str, workdir: Path) -> tuple[bytes, bytes | None]:
    """Returns the PDF and its .synctex.gz (None if the engine wrote none)."""
    engine_path = _find_engine(engine)
    stem = Path(main_tex).stem

    has_bib = any(f.suffix.lower() == ".bib" for f in workdir.glob("**/*.bib"))

    _run_latex_pass(engine_path, main_tex, workdir, stem)

    if has_bib:
        subprocess.run(
            ["bibtex", stem],
            capture_output=True,
            text=True,
            timeout=COMPILER_TIMEOUT,
            cwd=str(workdir),
        )

    _run_latex_pass(engine_path, main_tex, workdir, stem)
    _run_latex_pass(engine_path, main_tex, workdir, stem)

    pdf_path = workdir / f"{stem}.pdf"
    if not pdf_path.exists():
        raise RuntimeError("PDF file not generated")

    synctex_path = workdir / f"{stem}.synctex.gz"
    synctex = synctex_path.read_bytes() if synctex_path.exists() else None
    return pdf_path.read_bytes(), synctex


def process_compile(engine: str, main: str, files: list[dict], workdir: Path) -> tuple[bytes, bytes | None]:
    if not files:
        raise ValueError("No files to compile")

    if not main:
        detected = detect_main_tex(files)
        if detected is None:
            raise ValueError("Could not detect main .tex file")
        main = detected

    written = False
    main_written = False

    for f in files:
        raw_name = f.get("path") or f.get("name") or ""
        if not raw_name:
            raise ValueError("File entry missing 'path' or 'name'")
        content = f.get("content")
        base64_content = f.get("base64")

        filepath = resolve_file_path(workdir, raw_name)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if base64_content:
            filepath.write_bytes(b64.b64decode(base64_content))
        elif content is not None:
            filepath.write_text(content, encoding="utf-8")
        else:
            continue

        written = True
        if filepath.name == Path(main).name or str(filepath.relative_to(workdir)) == main:
            main_written = True

    if not written:
        raise ValueError("No files were written — all file entries may be empty")
    if not main_written:
        available = [f.get("path") or f.get("name") for f in files]
        raise ValueError(f"Main file '{main}' was not found in the files list. Available: {available}")

    return compile_latex(engine, main, workdir)


def convert_legacy_request(body: dict) -> tuple[str, str, list[dict]]:
    content = body.get("content", "")
    bibliography = body.get("bibliography", "")
    figures = body.get("figures", [])
    engine = body.get("engine", "pdflatex")

    files = [{"path": "main.tex", "content": content}]

    if bibliography:
        files.append({"path": "bibliography.bib", "content": bibliography})

    for fig in figures:
        name = fig.get("name", f"figure_{figures.index(fig)}")
        data = fig.get("data") or ""
        if "," in data:
            data = data.split(",", 1)[1]
        files.append({"path": f"figures/{name}", "base64": data})

    main = detect_main_tex(files) or "main.tex"
    return engine, main, files

