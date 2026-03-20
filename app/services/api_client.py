"""Async HTTP client for the StudioFace backend API."""

import asyncio
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class APIError:
    """Structured error response."""

    def __init__(self, message: str, code: str = "unknown", status: int = 0):
        self.message = message
        self.code = code
        self.status = status

    def to_dict(self) -> dict[str, Any]:
        return {"error": self.message, "code": self.code, "status": self.status}


class StudioFaceAPI:
    """Async client for the StudioFace backend API."""

    MAX_RETRIES = 3
    RETRY_CODES = {502, 503, 504}
    RETRY_DELAY = 1.0

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client

    @property
    def _auth_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with retry logic."""
        client = await self._get_client()
        url = path if path.startswith("http") else path

        headers = self._auth_headers.copy()
        if files:
            headers.pop("Content-Type", None)

        last_error: Optional[Exception] = None

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug("%s %s (attempt %d)", method, url, attempt + 1)
                response = await client.request(
                    method,
                    url,
                    json=json_data,
                    files=files,
                    params=params,
                    headers=headers,
                )
                if response.status_code in self.RETRY_CODES and attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

                if response.status_code >= 400:
                    try:
                        error_body = response.json()
                    except Exception:
                        error_body = {"detail": response.text}
                    return {
                        "error": error_body.get("detail", error_body.get("error", "Request failed")),
                        "code": str(response.status_code),
                        "status": response.status_code,
                    }

                if response.status_code == 204:
                    return {"success": True}

                try:
                    return response.json()
                except Exception:
                    return {"data": response.text}

            except httpx.TimeoutException:
                last_error = Exception("Request timed out")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
            except httpx.ConnectError:
                last_error = Exception("Connection failed")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
            except Exception as exc:
                last_error = exc
                break

        error_msg = str(last_error) if last_error else "Request failed after retries"
        return APIError(error_msg, "network_error").to_dict()

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # --- Health ---
    async def health_check(self) -> dict[str, Any]:
        return await self._request("GET", "/health/")

    # --- Auth ---
    async def send_magic_link(self, email: str) -> dict[str, Any]:
        return await self._request("POST", "/auth/magic-link", json_data={"email": email})

    async def verify_token(self, token: str) -> dict[str, Any]:
        return await self._request("POST", "/auth/verify", json_data={"token": token})

    async def get_microsoft_auth_url(self) -> dict[str, Any]:
        return await self._request("GET", "/auth/microsoft/url")

    async def get_current_user(self) -> dict[str, Any]:
        return await self._request("GET", "/auth/me")

    # --- Upload ---
    async def create_upload_session(self) -> dict[str, Any]:
        return await self._request("POST", "/upload/session")

    async def upload_file(
        self, session_id: str, file_bytes: bytes, filename: str
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/upload/{session_id}",
            files={"file": (filename, file_bytes)},
        )

    # --- Generations ---
    async def create_generation(
        self, session_id: str, style: str, presentation: str
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/generations/",
            json_data={
                "upload_session_id": session_id,
                "style": style,
                "presentation": presentation,
            },
        )

    async def get_generation(self, generation_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/generations/{generation_id}")

    async def get_generation_images(self, generation_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/generations/{generation_id}/images")

    async def list_generations(self) -> dict[str, Any]:
        return await self._request("GET", "/generations/")

    # --- Payments ---
    async def create_checkout(self, generation_id: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/checkout/",
            json_data={"generation_id": generation_id},
        )
