"""Unit tests for app.services.api_client — pure logic, no HTTP calls."""

from app.services.api_client import APIError, StudioFaceAPI


class TestStudioFaceAPIInit:
    """Constructor and property tests."""

    def test_client_initialization(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        assert api.base_url == "https://api.studioface.com"

    def test_base_url_trailing_slash_stripped(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com/")
        assert api.base_url == "https://api.studioface.com"

    def test_auth_headers_with_token(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        api.token = "test-token-123"
        headers = api._auth_headers
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token-123"
        assert headers["Content-Type"] == "application/json"

    def test_auth_headers_without_token(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        api.token = None
        headers = api._auth_headers
        assert "Authorization" not in headers
        assert headers["Content-Type"] == "application/json"


class TestAPIError:
    """APIError value object tests."""

    def test_api_error_to_dict(self) -> None:
        err = APIError(message="Not found", code="not_found", status=404)
        d = err.to_dict()
        assert d == {"error": "Not found", "code": "not_found", "status": 404}

    def test_api_error_defaults(self) -> None:
        err = APIError(message="Oops")
        d = err.to_dict()
        assert d["error"] == "Oops"
        assert d["code"] == "unknown"
        assert d["status"] == 0
