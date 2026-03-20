"""Global application state management."""

from typing import Any, Optional

import flet as ft

from app.services.api_client import StudioFaceAPI


class AppState:
    """Centralized state manager for the StudioFace app."""

    def __init__(self, page: ft.Page, api: StudioFaceAPI):
        self.page = page
        self.api = api

    @property
    def lang(self) -> str:
        return self.page.session.store.get("lang") or "en"

    @lang.setter
    def lang(self, value: str) -> None:
        self.page.session.store.set("lang", value)

    @property
    def user(self) -> Optional[dict[str, Any]]:
        return self.page.session.store.get("user")

    @user.setter
    def user(self, value: Optional[dict[str, Any]]) -> None:
        if value is None:
            try:
                self.page.session.store.remove("user")
            except Exception:
                pass
        else:
            self.page.session.store.set("user", value)

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    @property
    def current_generation_id(self) -> Optional[str]:
        return self.page.session.store.get("current_generation_id")

    @current_generation_id.setter
    def current_generation_id(self, value: Optional[str]) -> None:
        if value is None:
            try:
                self.page.session.store.remove("current_generation_id")
            except Exception:
                pass
        else:
            self.page.session.store.set("current_generation_id", value)

    @property
    def upload_session_id(self) -> Optional[str]:
        return self.page.session.store.get("upload_session_id")

    @upload_session_id.setter
    def upload_session_id(self, value: Optional[str]) -> None:
        if value is None:
            try:
                self.page.session.store.remove("upload_session_id")
            except Exception:
                pass
        else:
            self.page.session.store.set("upload_session_id", value)
