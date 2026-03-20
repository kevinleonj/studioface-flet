"""Generation service — create headshots and poll for completion."""

import asyncio
from typing import Any

from app.services.api_client import StudioFaceAPI

POLL_INTERVAL = 5  # seconds
MAX_POLL_ATTEMPTS = 120  # 10 minutes max


async def create_generation(
    api: StudioFaceAPI,
    style: str,
    upload_ids: list[str],
    presentation: str,
    upload_session_id: str,
) -> dict[str, Any]:
    """Create a new headshot generation.

    Args:
        api: API client instance.
        style: One of CORPORATE, STARTUP, TECH, BANKING, MEDICINE, CASUAL.
        upload_ids: List of upload UUIDs from upload_file().
        presentation: "masculine" or "feminine".
        upload_session_id: Session UUID from create_upload_session().
    """
    return await api.create_generation(style, upload_ids, presentation, upload_session_id)


async def poll_generation(
    api: StudioFaceAPI,
    generation_id: str,
    on_update: Any = None,
) -> dict[str, Any]:
    """Poll generation status until complete or failed."""
    for _ in range(MAX_POLL_ATTEMPTS):
        result = await api.get_generation(generation_id)
        if "error" in result:
            return result

        status = result.get("status", "").lower()

        if on_update:
            await on_update(result)

        if status in ("completed", "complete", "done"):
            return result
        if status in ("failed", "error"):
            return {
                "error": result.get("error", "Generation failed"),
                "code": "generation_failed",
                "status": 500,
            }

        await asyncio.sleep(POLL_INTERVAL)

    return {"error": "Generation timed out", "code": "timeout", "status": 408}


async def get_images(
    api: StudioFaceAPI, generation_id: str
) -> dict[str, Any]:
    """Get the generated images for a generation.

    Images are included in the generation detail response when status=completed.
    """
    return await api.get_generation(generation_id)
