from pathlib import Path
from email.header import decode_header
import re
import uuid
from typing import Dict

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ..services import FileStorage

router = APIRouter(prefix="/api", tags=["upload"])

storage = FileStorage()

ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt"}
CONTENT_TYPE_EXTENSIONS = {
    "application/pdf": ".pdf",
    "text/markdown": ".md",
    "text/plain": ".txt",
}
WINDOWS_RESERVED_CHARS = r'<>:"/\|?*'


def _decode_filename(filename: str = "") -> str:
    """Decode RFC 2047 filenames sometimes produced by multipart clients."""
    raw = str(filename or "").strip()
    if not raw:
        return ""

    try:
        parts = decode_header(raw)
        decoded = []
        for value, charset in parts:
            if isinstance(value, bytes):
                decoded.append(value.decode(charset or "utf-8", errors="replace"))
            else:
                decoded.append(value)
        candidate = "".join(decoded).strip()
        return candidate or raw
    except Exception:
        return raw


def _safe_path_name(filename: str, fallback_ext: str) -> str:
    """Keep display-friendly names out of unsafe filesystem paths."""
    decoded = _decode_filename(filename)
    for char in WINDOWS_RESERVED_CHARS:
        decoded = decoded.replace(char, "_")
    decoded = decoded.strip().strip(".")

    if not decoded:
        decoded = f"uploaded{fallback_ext}"

    if not _detect_extension(decoded, "") and fallback_ext:
        decoded = f"{decoded}{fallback_ext}"

    return decoded


def _detect_extension(filename: str = "", content_type: str = "") -> str:
    """Detect a whitelisted extension, including non-ASCII filename fallbacks."""
    filename_str = _decode_filename(filename)
    ext = Path(filename_str).suffix.lower()

    if not ext:
        match = re.search(r"(\.[A-Za-z0-9]+)$", filename_str)
        if match:
            ext = match.group(1).lower()

    if not ext:
        normalized_type = (content_type or "").split(";")[0].strip().lower()
        ext = CONTENT_TYPE_EXTENSIONS.get(normalized_type, "")

    return ext


def _file_type_from_extension(ext: str) -> str:
    if ext == ".pdf":
        return "pdf"
    if ext in {".md", ".markdown"}:
        return "markdown"
    if ext == ".txt":
        return "txt"
    raise ValueError(f"Unsupported file type: {ext}")


async def _save_temp_file(file: UploadFile, filename: str) -> str:
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / f"{uuid.uuid4().hex}_{filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    return str(temp_path)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict:
    """Upload a PDF, Markdown, or plain text textbook file."""
    try:
        filename = _decode_filename(file.filename) or "uploaded"
        file_ext = _detect_extension(filename, file.content_type or "")

        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        max_size = 100 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {max_size / 1024 / 1024:.0f}MB",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        textbook_id = f"textbook_{uuid.uuid4().hex[:12]}"
        file_type = _file_type_from_extension(file_ext)

        temp_name = _safe_path_name(filename, file_ext)
        temp_path = await _save_temp_file(file, temp_name)
        saved_path = storage.save_uploaded_file(temp_path, temp_name)

        metadata = {
            "filename": temp_name,
            "title": Path(temp_name).stem,
            "file_type": file_type,
            "file_path": saved_path,
            "file_size": file_size,
            "total_pages": 0,
        }

        storage.save_parse_result(textbook_id, [], metadata)

        return {
            "status": "success",
            "message": "File uploaded successfully",
            "data": {
                "textbook_id": textbook_id,
                "filename": metadata["filename"],
                "file_type": file_type,
                "file_size": file_size,
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {exc}",
        ) from exc
