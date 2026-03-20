"""Upload service — file validation and upload handling."""

from typing import Any

from app.services.api_client import StudioFaceAPI

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_FILES = 2
MAX_FILES = 5


def validate_file(filename: str, size: int) -> str | None:
    """Validate a file. Returns error key or None if valid."""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return "create.invalid_format"
    if size > MAX_FILE_SIZE:
        return "create.file_too_large"
    return None


def validate_file_count(count: int) -> str | None:
    """Validate the number of files. Returns error key or None."""
    if count < MIN_FILES:
        return "create.min_photos"
    if count > MAX_FILES:
        return "create.max_photos"
    return None


async def create_session_and_upload(
    api: StudioFaceAPI,
    files: list[tuple[str, bytes]],
) -> dict[str, Any]:
    """Create an upload session and upload all files.

    Returns {"session_id": str, "upload_ids": list[str], "uploaded": list[dict]}.
    """
    session_result = await api.create_upload_session()
    if "error" in session_result:
        return session_result

    session_id = session_result.get("session_id") or session_result.get("id", "")

    uploaded = []
    upload_ids: list[str] = []
    for filename, file_bytes in files:
        result = await api.upload_file(file_bytes, filename, session_id)
        if "error" in result:
            return result
        uploaded.append(result)
        upload_id = result.get("id", "")
        if upload_id:
            upload_ids.append(upload_id)

    return {"session_id": session_id, "upload_ids": upload_ids, "uploaded": uploaded}
