"""Extractor determinista de texto, metadatos y huellas SHA-256 sin modificar archivos originales."""

import hashlib
import mimetypes
from pathlib import Path

from docx import Document
from openpyxl import load_workbook
from pypdf import PdfReader

from app.db.models import ExtractionStatus, FileCategory


TEXT_EXTENSIONS = {".md", ".txt", ".py", ".html", ".htm", ".json", ".css", ".js", ".ts", ".csv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".rar"}


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
    if ext in {".py", ".html", ".htm", ".js", ".ts", ".css"}:
        return FileCategory.SOURCE_CODE, mime
    if ext in {".xlsx", ".json", ".csv"}:
        return FileCategory.DATA_TABLE, mime
    if ext in IMAGE_EXTENSIONS:
        return FileCategory.IMAGE_DIAGRAM, mime
    if ext in VIDEO_EXTENSIONS:
        return FileCategory.VIDEO, mime
    return FileCategory.ARCHIVE, mime


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
