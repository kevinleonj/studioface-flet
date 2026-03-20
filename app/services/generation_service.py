"""Generation service — create headshots and poll for completion."""

import asyncio
from typing import Any

from app.services.api_client import StudioFaceAPI

POLL_INTERVAL = 5  # seconds
MAX_POLL_ATTEMPTS = 120  # 10 minutes max


async def create_generation(
    api: StudioFaceAPI,
    session_id: str,
    style: str,
    presentation: str,
) -> dict[str, Any]:
    """Create a new headshot generation."""
    return await api.create_generation(session_id, style, presentation)


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
    """Get the generated images for a generation."""
    return await api.get_generation_images(generation_id)
