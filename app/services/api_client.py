"""Async HTTP client for the StudioFace backend API.

Matches the real production API at https://api.studioface.app/api/v1.
All paths, payloads, and auth flows verified against live endpoints 2026-03-20.
"""

import asyncio
import logging
from typing import Any, Callable, Optional

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
    """Async client for the StudioFace backend API.

    Endpoints match production at https://api.studioface.app/api/v1.
    Includes automatic 401 token refresh and retry logic.
    """

    MAX_RETRIES = 3
    RETRY_CODES = {502, 503, 504}
    RETRY_DELAY = 1.0

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self._refresh_token_value: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._on_tokens_refreshed: Optional[Callable[[str, str], Any]] = None

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """Store both access and refresh tokens."""
        self.token = access_token
        self._refresh_token_value = refresh_token

    def clear_tokens(self) -> None:
        """Clear all stored tokens."""
        self.token = None
        self._refresh_token_value = None

    def on_tokens_refreshed(self, callback: Callable[[str, str], Any]) -> None:
        """Register a callback for when tokens are auto-refreshed.

        The callback receives (new_access_token, new_refresh_token).
        Use this to persist the new tokens to client_storage.
        """
        self._on_tokens_refreshed = callback

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

    def _normalize_error(self, response: httpx.Response) -> dict[str, Any]:
        """Normalize both backend error formats into a consistent dict.

        Backend returns either:
          {"detail": "..."} or {"detail": [{"msg": "...", ...}]}  (FastAPI)
          {"error": {"code": "...", "message": "...", "details": {}}}  (Custom)
        """
        try:
            body = response.json()
        except Exception:
            return {
                "error": response.text or "Request failed",
                "code": str(response.status_code),
                "status": response.status_code,
            }

        # Custom error format: {"error": {"code": ..., "message": ...}}
        if isinstance(body.get("error"), dict):
            err = body["error"]
            return {
                "error": err.get("message", "Request failed"),
                "code": err.get("code", str(response.status_code)),
                "status": response.status_code,
            }

        # FastAPI detail (string)
        if isinstance(body.get("detail"), str):
            return {
                "error": body["detail"],
                "code": str(response.status_code),
                "status": response.status_code,
            }

        # FastAPI validation detail (list)
        if isinstance(body.get("detail"), list):
            messages = [item.get("msg", "") for item in body["detail"] if isinstance(item, dict)]
            return {
                "error": "; ".join(messages) if messages else "Validation error",
                "code": "validation_error",
                "status": response.status_code,
            }

        # Fallback
        return {
            "error": body.get("detail", body.get("error", "Request failed")),
            "code": str(response.status_code),
            "status": response.status_code,
        }

    async def _try_refresh(self) -> bool:
        """Attempt to refresh the access token using the stored refresh token.

        Returns True if refresh succeeded and tokens were updated.
        """
        if not self._refresh_token_value:
            return False

        try:
            client = await self._get_client()
            response = await client.request(
                "POST",
                "/auth/refresh",
                json={"refresh_token": self._refresh_token_value},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                data = response.json()
                new_access = data.get("access_token", data.get("token", ""))
                new_refresh = data.get("refresh_token", self._refresh_token_value)
                if new_access:
                    self.token = new_access
                    self._refresh_token_value = new_refresh
                    if self._on_tokens_refreshed:
                        self._on_tokens_refreshed(new_access, new_refresh)
                    logger.info("Token refreshed successfully")
                    return True
            logger.warning("Token refresh failed: %d", response.status_code)
            return False
        except Exception as exc:
            logger.warning("Token refresh error: %s", exc)
            return False

    async def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        _is_retry: bool = False,
    ) -> dict[str, Any]:
        """Make an HTTP request with retry and token-refresh logic.

        On 401, automatically attempts a token refresh and retries once.
        On 502/503/504, retries up to MAX_RETRIES with backoff.
        """
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
                    data=data,
                    files=files,
                    params=params,
                    headers=headers,
                )

                # Retry on gateway errors
                if response.status_code in self.RETRY_CODES and attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

                # Auto-refresh on 401 (only once, not on refresh/login endpoints)
                if (
                    response.status_code == 401
                    and not _is_retry
                    and path not in ("/auth/refresh", "/auth/magic-link/verify", "/auth/microsoft/callback")
                ):
                    refreshed = await self._try_refresh()
                    if refreshed:
                        return await self._request(
                            method, path, json_data=json_data, data=data,
                            files=files, params=params, _is_retry=True,
                        )

                if response.status_code >= 400:
                    return self._normalize_error(response)

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
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ------------------------------------------------------------------ #
    # Health                                                               #
    # ------------------------------------------------------------------ #

    async def health_check(self) -> dict[str, Any]:
        """GET /health/ — no auth required."""
        return await self._request("GET", "/health/")

    # ------------------------------------------------------------------ #
    # Auth                                                                 #
    # ------------------------------------------------------------------ #

    async def send_magic_link(self, email: str, locale: str = "en") -> dict[str, Any]:
        """POST /auth/magic-link — send a magic-link sign-in email.

        Args:
            email: User's email address.
            locale: Language code for the email template (e.g. "en", "de", "fr").
        """
        return await self._request(
            "POST", "/auth/magic-link", json_data={"email": email, "locale": locale}
        )

    async def verify_token(self, token: str) -> dict[str, Any]:
        """POST /auth/magic-link/verify — verify magic-link token (min 32 chars).

        Returns user info + auth tokens on success.
        """
        return await self._request(
            "POST", "/auth/magic-link/verify", json_data={"token": token}
        )

    async def get_microsoft_auth_url(self) -> dict[str, Any]:
        """GET /auth/microsoft/url — get Microsoft OAuth authorization URL.

        Returns {"auth_url": "https://login.microsoftonline.com/..."}.
        """
        return await self._request("GET", "/auth/microsoft/url")

    async def microsoft_callback(self, code: str, state: str) -> dict[str, Any]:
        """POST /auth/microsoft/callback — exchange OAuth code for tokens.

        Args:
            code: Authorization code from Microsoft redirect.
            state: State parameter for CSRF verification.

        Returns user info + auth tokens on success.
        """
        return await self._request(
            "POST", "/auth/microsoft/callback", json_data={"code": code, "state": state}
        )

    async def get_current_user(self) -> dict[str, Any]:
        """GET /auth/me — get the authenticated user's profile.

        Requires Bearer token. Returns {"id", "email", "name"}.
        """
        return await self._request("GET", "/auth/me")

    async def update_gdpr_consent(self, consent: bool) -> dict[str, Any]:
        """PUT /auth/gdpr-consent — update GDPR consent status.

        Args:
            consent: Whether the user consents to data processing.
        """
        return await self._request(
            "PUT", "/auth/gdpr-consent", json_data={"consent": consent}
        )

    async def refresh_auth_token(self, refresh_token: str) -> dict[str, Any]:
        """POST /auth/refresh — refresh an expired access token.

        Args:
            refresh_token: The refresh token from initial auth.

        Returns new access_token and refresh_token on success.
        """
        return await self._request(
            "POST", "/auth/refresh", json_data={"refresh_token": refresh_token}
        )

    async def logout(self, refresh_token: Optional[str] = None) -> dict[str, Any]:
        """POST /auth/logout — log out and invalidate tokens.

        Requires Bearer token header AND refresh_token in body.

        Args:
            refresh_token: The refresh token to invalidate. Falls back to stored value.
        """
        token = refresh_token or self._refresh_token_value
        body: dict[str, Any] = {}
        if token:
            body["refresh_token"] = token
        return await self._request("POST", "/auth/logout", json_data=body if body else None)

    # ------------------------------------------------------------------ #
    # Uploads                                                              #
    # ------------------------------------------------------------------ #

    async def create_upload_session(self) -> dict[str, Any]:
        """POST /uploads/sessions — create a new upload session.

        Returns {"id": "session-uuid", ...}.
        """
        return await self._request("POST", "/uploads/sessions")

    async def upload_file(
        self, file_content: bytes, filename: str, upload_session_id: str
    ) -> dict[str, Any]:
        """POST /uploads/ — upload a photo file.

        Uses multipart/form-data with:
          - file: the binary image data
          - upload_session_id: the session UUID from create_upload_session()

        Args:
            file_content: Raw bytes of the image file.
            filename: Original filename (e.g. "photo.jpg").
            upload_session_id: Session ID from create_upload_session().

        Returns {"id": "upload-uuid", ...}.
        """
        return await self._request(
            "POST",
            "/uploads/",
            data={"upload_session_id": upload_session_id},
            files={"file": (filename, file_content)},
        )

    # ------------------------------------------------------------------ #
    # Generations                                                          #
    # ------------------------------------------------------------------ #

    async def create_generation(
        self,
        style: str,
        upload_ids: list[str],
        presentation: str,
        upload_session_id: str,
    ) -> dict[str, Any]:
        """POST /generations/ — create a new headshot generation job.

        Args:
            style: One of CORPORATE, STARTUP, TECH, BANKING, MEDICINE, CASUAL.
            upload_ids: List of upload UUIDs from upload_file().
            presentation: "masculine" or "feminine".
            upload_session_id: Session UUID from create_upload_session().

        Returns {"id": "generation-uuid", "status": "pending", ...}.
        """
        return await self._request(
            "POST",
            "/generations/",
            json_data={
                "style": style,
                "upload_ids": upload_ids,
                "presentation": presentation,
                "upload_session_id": upload_session_id,
            },
        )

    async def get_generation(self, generation_id: str) -> dict[str, Any]:
        """GET /generations/{id} — get generation status and details.

        Status values: pending, processing, completed, failed.
        When completed, includes image URLs.
        """
        return await self._request("GET", f"/generations/{generation_id}")

    async def list_generations(
        self, page: int = 1, page_size: int = 10
    ) -> dict[str, Any]:
        """GET /generations/ — list user's generations with pagination.

        Args:
            page: Page number (1-based).
            page_size: Number of items per page.
        """
        return await self._request(
            "GET", "/generations/", params={"page": page, "page_size": page_size}
        )

    # ------------------------------------------------------------------ #
    # Payments                                                             #
    # ------------------------------------------------------------------ #

    async def create_checkout(
        self, generation_id: str, currency: str = "EUR"
    ) -> dict[str, Any]:
        """POST /payments/checkout — create a Stripe checkout session.

        Args:
            generation_id: The generation to pay for.
            currency: Payment currency (e.g. "EUR", "USD").

        Returns {"checkout_url": "https://checkout.stripe.com/...", "session_id": "cs_live_..."}.
        """
        return await self._request(
            "POST",
            "/payments/checkout",
            json_data={"generation_id": generation_id, "currency": currency},
        )

    async def list_payments(self) -> dict[str, Any]:
        """GET /payments/ — list payment history for the authenticated user."""
        return await self._request("GET", "/payments/")

    # ------------------------------------------------------------------ #
    # User Settings                                                        #
    # ------------------------------------------------------------------ #

    async def update_locale(self, locale: str) -> dict[str, Any]:
        """PUT /users/me/locale — update the user's preferred language.

        Args:
            locale: Language code (e.g. "en", "de", "fr").
        """
        return await self._request(
            "PUT", "/users/me/locale", json_data={"locale": locale}
        )

    async def export_data(self) -> dict[str, Any]:
        """POST /users/me/export — request a GDPR data export."""
        return await self._request("POST", "/users/me/export")

    async def delete_account(self) -> dict[str, Any]:
        """DELETE /users/me — permanently delete the user's account."""
        return await self._request("DELETE", "/users/me")
