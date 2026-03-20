"""Unit tests for app.services.api_client — pure logic, no HTTP calls."""

from unittest.mock import MagicMock

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


class TestTokenManagement:
    """Token storage and lifecycle tests."""

    def test_set_tokens(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        api.set_tokens("access-123", "refresh-456")
        assert api.token == "access-123"
        assert api._refresh_token_value == "refresh-456"

    def test_clear_tokens(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        api.set_tokens("access-123", "refresh-456")
        api.clear_tokens()
        assert api.token is None
        assert api._refresh_token_value is None

    def test_on_tokens_refreshed_callback(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        callback = MagicMock()
        api.on_tokens_refreshed(callback)
        assert api._on_tokens_refreshed is callback


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


class TestErrorNormalization:
    """Test _normalize_error handles both backend error formats."""

    def _make_response(self, status: int, json_body: dict) -> MagicMock:
        """Create a mock httpx.Response."""
        resp = MagicMock()
        resp.status_code = status
        resp.json.return_value = json_body
        resp.text = str(json_body)
        return resp

    def test_custom_error_format(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        resp = self._make_response(401, {
            "error": {"code": "AUTH_FAILED", "message": "Not authenticated", "details": {}}
        })
        result = api._normalize_error(resp)
        assert result["error"] == "Not authenticated"
        assert result["code"] == "AUTH_FAILED"
        assert result["status"] == 401

    def test_fastapi_string_detail(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        resp = self._make_response(404, {"detail": "Not found"})
        result = api._normalize_error(resp)
        assert result["error"] == "Not found"
        assert result["code"] == "404"
        assert result["status"] == 404

    def test_fastapi_validation_detail(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        resp = self._make_response(422, {
            "detail": [
                {"type": "value_error", "loc": ["body", "email"], "msg": "invalid email"}
            ]
        })
        result = api._normalize_error(resp)
        assert result["error"] == "invalid email"
        assert result["code"] == "validation_error"
        assert result["status"] == 422

    def test_fallback_when_json_fails(self) -> None:
        api = StudioFaceAPI("https://api.studioface.com")
        resp = MagicMock()
        resp.status_code = 500
        resp.json.side_effect = ValueError("not json")
        resp.text = "Internal Server Error"
        result = api._normalize_error(resp)
        assert result["error"] == "Internal Server Error"
        assert result["status"] == 500


class TestMethodSignatures:
    """Verify method signatures match production API requirements."""

    def test_send_magic_link_has_locale_param(self) -> None:
        """send_magic_link must accept locale parameter."""
        import inspect
        sig = inspect.signature(StudioFaceAPI.send_magic_link)
        params = list(sig.parameters.keys())
        assert "email" in params
        assert "locale" in params

    def test_send_magic_link_locale_defaults_to_en(self) -> None:
        import inspect
        sig = inspect.signature(StudioFaceAPI.send_magic_link)
        assert sig.parameters["locale"].default == "en"

    def test_microsoft_callback_method_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "microsoft_callback")
        import inspect
        sig = inspect.signature(StudioFaceAPI.microsoft_callback)
        params = list(sig.parameters.keys())
        assert "code" in params
        assert "state" in params

    def test_update_gdpr_consent_method_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "update_gdpr_consent")
        import inspect
        sig = inspect.signature(StudioFaceAPI.update_gdpr_consent)
        assert "consent" in sig.parameters

    def test_refresh_auth_token_method_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "refresh_auth_token")
        import inspect
        sig = inspect.signature(StudioFaceAPI.refresh_auth_token)
        assert "refresh_token" in sig.parameters

    def test_logout_accepts_refresh_token(self) -> None:
        import inspect
        sig = inspect.signature(StudioFaceAPI.logout)
        assert "refresh_token" in sig.parameters

    def test_create_generation_full_payload(self) -> None:
        """create_generation must accept style, upload_ids, presentation, upload_session_id."""
        import inspect
        sig = inspect.signature(StudioFaceAPI.create_generation)
        params = list(sig.parameters.keys())
        assert "style" in params
        assert "upload_ids" in params
        assert "presentation" in params
        assert "upload_session_id" in params

    def test_list_generations_pagination(self) -> None:
        import inspect
        sig = inspect.signature(StudioFaceAPI.list_generations)
        params = sig.parameters
        assert "page" in params
        assert "page_size" in params
        assert params["page"].default == 1
        assert params["page_size"].default == 10

    def test_create_checkout_has_currency(self) -> None:
        import inspect
        sig = inspect.signature(StudioFaceAPI.create_checkout)
        params = sig.parameters
        assert "generation_id" in params
        assert "currency" in params
        assert params["currency"].default == "EUR"

    def test_upload_file_method_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "upload_file")
        import inspect
        sig = inspect.signature(StudioFaceAPI.upload_file)
        params = list(sig.parameters.keys())
        assert "file_content" in params
        assert "filename" in params
        assert "upload_session_id" in params

    def test_create_upload_session_method_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "create_upload_session")


class TestUserEndpoints:
    """Verify user settings methods exist with correct signatures."""

    def test_update_locale_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "update_locale")
        import inspect
        sig = inspect.signature(StudioFaceAPI.update_locale)
        assert "locale" in sig.parameters

    def test_export_data_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "export_data")

    def test_delete_account_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "delete_account")

    def test_list_payments_exists(self) -> None:
        assert hasattr(StudioFaceAPI, "list_payments")


class TestRemovedObsoleteMethods:
    """Verify old incorrect methods are removed."""

    def test_no_get_payment_plans(self) -> None:
        """get_payment_plans was never in the real API contract."""
        assert not hasattr(StudioFaceAPI, "get_payment_plans")

    def test_no_get_payment_history(self) -> None:
        assert not hasattr(StudioFaceAPI, "get_payment_history")

    def test_no_get_credits(self) -> None:
        assert not hasattr(StudioFaceAPI, "get_credits")

    def test_no_get_generation_images_separate(self) -> None:
        """Images come back in get_generation(), no separate endpoint needed."""
        assert not hasattr(StudioFaceAPI, "get_generation_images")

    def test_no_get_generation_status_separate(self) -> None:
        assert not hasattr(StudioFaceAPI, "get_generation_status")

    def test_no_download_generation(self) -> None:
        assert not hasattr(StudioFaceAPI, "download_generation")

    def test_no_get_generation_history(self) -> None:
        assert not hasattr(StudioFaceAPI, "get_generation_history")
