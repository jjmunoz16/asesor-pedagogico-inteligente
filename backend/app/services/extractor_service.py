"""Extractor determinista de texto, metadatos, ZIP seguro y detección de inyección de prompts."""

import hashlib
import mimetypes
from pathlib import Path
import re
import zipfile

from docx import Document
from openpyxl import load_workbook
from pypdf import PdfReader

from app.db.models import ExtractionStatus, FileCategory


TEXT_EXTENSIONS = {".md", ".txt", ".py", ".html", ".htm", ".json", ".css", ".js", ".ts", ".csv", ".ipynb"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".rar"}

MAX_ZIP_ENTRIES = 100
MAX_ZIP_UNCOMPRESSED_BYTES = 15 * 1024 * 1024

_PROMPT_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"ignora\s+(todas\s+)?las\s+instrucciones", re.IGNORECASE),
    re.compile(r"disregard\s+system\s+prompt", re.IGNORECASE),
    re.compile(r"(asigna|give|pon|set)\s+(a\s+)?(calificaci[oó]n|score|nota)\s*(de|=|:)?\s*5(\.0+)?", re.IGNORECASE),
    re.compile(r"</untrusted_student_evidence>", re.IGNORECASE),
)


def detect_prompt_injection_signals(text: str) -> list[str]:
    """Detecta intentos explícitos de prompt injection dentro de documentos estudiantiles."""
    if not text:
        return []
    hits: list[str] = []
    for pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            hits.append(f"Patrón sospechoso de inyección de instrucciones detectado: '{pattern.pattern[:48]}'")
    return hits


def compute_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def compute_sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def classify_file(path: Path) -> tuple[FileCategory, str]:
    ext = path.suffix.lower()
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "application/octet-stream"

    if ext == ".pdf":
        return FileCategory.REPORT_PDF, "application/pdf"
    if ext == ".docx":
        return (
            FileCategory.REPORT_DOCX,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    if ext in {".md", ".txt"}:
        return FileCategory.MARKDOWN, mime
    if ext in {".py", ".html", ".htm", ".js", ".ts", ".css", ".ipynb"}:
        return FileCategory.SOURCE_CODE, mime
    if ext in {".xlsx", ".json", ".csv"}:
        return FileCategory.DATA_TABLE, mime
    if ext in IMAGE_EXTENSIONS:
        return FileCategory.IMAGE_DIAGRAM, mime
    if ext in VIDEO_EXTENSIONS:
        return FileCategory.VIDEO, mime
    return FileCategory.ARCHIVE, mime


def _extract_zip_summary(path: Path, max_chars: int) -> tuple[str, ExtractionStatus]:
    """Inspecciona archivos ZIP de forma segura (anti-Zip-Bomb y anti-Path-Traversal)."""
    with zipfile.ZipFile(path, "r") as zf:
        infos = zf.infolist()
        if len(infos) > MAX_ZIP_ENTRIES:
            return (
                f"Archivo ZIP excede el límite seguro de entradas ({len(infos)} > {MAX_ZIP_ENTRIES}).",
                ExtractionStatus.PARTIAL_METADATA_ONLY,
            )

        total_uncompressed = 0
        parts: list[str] = []
        listed_names: list[str] = []
        for info in infos:
            member_name = info.filename.replace("\\", "/")
            if member_name.startswith("/") or ".." in member_name.split("/"):
                return (
                    f"Archivo ZIP rechazado por ruta insegura (path traversal): '{info.filename}'.",
                    ExtractionStatus.UNSUPPORTED,
                )
            total_uncompressed += max(0, info.file_size)
            if total_uncompressed > MAX_ZIP_UNCOMPRESSED_BYTES:
                return (
                    "Archivo ZIP excede el límite seguro de descompresión (posible Zip Bomb).",
                    ExtractionStatus.PARTIAL_METADATA_ONLY,
                )
            if info.is_dir():
                continue
            listed_names.append(member_name)
            ext = Path(member_name).suffix.lower()
            if ext in {".py", ".md", ".txt", ".json", ".html", ".csv"} and info.file_size <= 250_000:
                with zf.open(info, "r") as member_fh:
                    raw = member_fh.read(min(info.file_size, 4096))
                snippet = raw.decode("utf-8", errors="replace").strip()
                if snippet:
                    parts.append(f"[ZIP:{member_name}]\n{snippet[:1500]}")

        if parts:
            header = f"Archivo ZIP válido ({len(listed_names)} archivos: {', '.join(listed_names[:10])}).\n\n"
            return (header + "\n\n".join(parts))[:max_chars], ExtractionStatus.EXTRACTED
        if listed_names:
            return (
                f"Archivo ZIP inspeccionado ({len(listed_names)} archivos: {', '.join(listed_names[:12])}).",
                ExtractionStatus.PARTIAL_METADATA_ONLY,
            )
        return "Archivo ZIP vacío.", ExtractionStatus.PARTIAL_METADATA_ONLY


def extract_content_from_path(path: Path, max_chars: int = 12000) -> tuple[str, ExtractionStatus]:
    """Extrae texto legible cuando el formato lo soporta; nunca inventa contenido."""
    ext = path.suffix.lower()
    try:
        if ext == ".pdf":
            reader = PdfReader(str(path))
            parts: list[str] = []
            for idx, page in enumerate(reader.pages, start=1):
                txt = (page.extract_text() or "").strip()
                if txt:
                    parts.append(f"[Página {idx}]\n{txt}")
            joined = "\n\n".join(parts)
            if joined:
                return joined[:max_chars], ExtractionStatus.EXTRACTED
            return (
                f"PDF sin texto extraíble ({len(reader.pages)} páginas; posible PDF escaneado).",
                ExtractionStatus.PARTIAL_METADATA_ONLY,
            )

        if ext == ".docx":
            doc = Document(str(path))
            lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    cells = [c.text.strip().replace("\n", " ") for c in row.cells if c.text.strip()]
                    if cells:
                        lines.append(" | ".join(cells))
            joined = "\n".join(lines)
            return (joined[:max_chars], ExtractionStatus.EXTRACTED) if joined else (
                "Documento DOCX vacío.",
                ExtractionStatus.PARTIAL_METADATA_ONLY,
            )

        if ext == ".xlsx":
            wb = load_workbook(str(path), data_only=True, read_only=True)
            lines: list[str] = []
            for sheet in wb.worksheets:
                lines.append(f"[Hoja: {sheet.title}]")
                for row in sheet.iter_rows(values_only=True):
                    vals = [str(v).strip() for v in row if v is not None and str(v).strip()]
                    if vals:
                        lines.append(" | ".join(vals))
            wb.close()
            joined = "\n".join(lines)
            return (joined[:max_chars], ExtractionStatus.EXTRACTED) if joined else (
                "Libro XLSX sin celdas con texto.",
                ExtractionStatus.PARTIAL_METADATA_ONLY,
            )

        if ext == ".zip":
            return _extract_zip_summary(path, max_chars=max_chars)

        if ext in TEXT_EXTENSIONS:
            raw = path.read_text(encoding="utf-8", errors="replace")
            return raw[:max_chars], ExtractionStatus.EXTRACTED

        if ext in IMAGE_EXTENSIONS:
            size_kb = round(path.stat().st_size / 1024, 1)
            return (
                f"Archivo de imagen/diagrama ({ext}, {size_kb} KB). Disponible para inspección visual o multimodal.",
                ExtractionStatus.PARTIAL_METADATA_ONLY,
            )

        if ext in VIDEO_EXTENSIONS:
            size_mb = round(path.stat().st_size / (1024 * 1024), 2)
            return (
                f"Archivo de video ({ext}, {size_mb} MB). Transcripción automática no ejecutada; no se debe inferir contenido oral no verificado.",
                ExtractionStatus.PARTIAL_METADATA_ONLY,
            )

        size_kb = round(path.stat().st_size / 1024, 1)
        return (
            f"Archivo empaquetado/binario ({ext or 'sin extensión'}, {size_kb} KB).",
            ExtractionStatus.PARTIAL_METADATA_ONLY,
        )
    except Exception as exc:
        return f"No fue posible extraer texto del archivo ({exc.__class__.__name__}).", ExtractionStatus.UNSUPPORTED
