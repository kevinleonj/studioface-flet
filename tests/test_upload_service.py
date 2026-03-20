"""Unit tests for app.services.upload_service — file validation logic."""

from app.services.upload_service import validate_file, validate_file_count


class TestValidateFile:
    """validate_file returns None on success, error key on failure."""

    def test_validate_valid_jpg(self) -> None:
        assert validate_file("photo.jpg", 1000) is None

    def test_validate_valid_png(self) -> None:
        assert validate_file("photo.png", 1000) is None

    def test_validate_valid_jpeg(self) -> None:
        assert validate_file("photo.jpeg", 1000) is None

    def test_validate_invalid_extension(self) -> None:
        result = validate_file("photo.gif", 1000)
        assert result is not None
        assert result == "create.invalid_format"

    def test_validate_too_large(self) -> None:
        result = validate_file("photo.jpg", 11 * 1024 * 1024)
        assert result is not None
        assert result == "create.file_too_large"


class TestValidateFileCount:
    """validate_file_count returns None on success, error key on failure."""

    def test_validate_count_too_few(self) -> None:
        result = validate_file_count(1)
        assert result is not None
        assert result == "create.min_photos"

    def test_validate_count_too_many(self) -> None:
        result = validate_file_count(6)
        assert result is not None
        assert result == "create.max_photos"

    def test_validate_count_valid(self) -> None:
        assert validate_file_count(3) is None
