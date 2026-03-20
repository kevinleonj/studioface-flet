"""Unit tests for app.i18n — translation completeness, interpolation, fallback."""

import re

from app.i18n import LANGUAGES, TRANSLATIONS, t


class TestTranslationCompleteness:
    """Every language must have the same set of keys."""

    def test_all_languages_have_all_keys(self) -> None:
        en_keys = set(TRANSLATIONS["en"].keys())
        es_keys = set(TRANSLATIONS["es"].keys())
        de_keys = set(TRANSLATIONS["de"].keys())

        missing_in_es = en_keys - es_keys
        missing_in_de = en_keys - de_keys
        extra_in_es = es_keys - en_keys
        extra_in_de = de_keys - en_keys

        assert not missing_in_es, f"Keys missing in ES: {missing_in_es}"
        assert not missing_in_de, f"Keys missing in DE: {missing_in_de}"
        assert not extra_in_es, f"Extra keys in ES not in EN: {extra_in_es}"
        assert not extra_in_de, f"Extra keys in DE not in EN: {extra_in_de}"

    def test_no_empty_translations(self) -> None:
        for lang, translations in TRANSLATIONS.items():
            for key, value in translations.items():
                assert value != "", f"Empty translation: {lang}.{key}"

    def test_no_untranslated_keys(self) -> None:
        for lang, translations in TRANSLATIONS.items():
            for key, value in translations.items():
                assert value != key, (
                    f"Translation value equals its key (likely untranslated): "
                    f"{lang}.{key} = '{value}'"
                )

    def test_key_count_minimum(self) -> None:
        for lang, translations in TRANSLATIONS.items():
            count = len(translations)
            assert count >= 80, (
                f"Language '{lang}' only has {count} keys, expected >= 80"
            )


class TestInterpolation:
    """Variable substitution via str.format() kwargs."""

    def test_interpolation(self) -> None:
        result = t("create.uploaded_count", lang="en", count=3)
        assert result == "3 photo(s) uploaded"

    def test_interpolation_spanish(self) -> None:
        result = t("create.uploaded_count", lang="es", count=3)
        assert result == "3 foto(s) subida(s)"

    def test_interpolation_german(self) -> None:
        result = t("create.uploaded_count", lang="de", count=3)
        assert result == "3 Foto(s) hochgeladen"


class TestFallbackAndMissing:
    """Fallback to English for unknown langs; return key for missing keys."""

    def test_fallback_to_english(self) -> None:
        result = t("hero.title", lang="fr")
        assert result == TRANSLATIONS["en"]["hero.title"]

    def test_missing_key_returns_key(self) -> None:
        result = t("nonexistent.key", lang="en")
        assert result == "nonexistent.key"


class TestLanguagesDict:
    """LANGUAGES metadata dict must list all supported languages."""

    def test_all_languages_defined(self) -> None:
        assert "en" in LANGUAGES
        assert "es" in LANGUAGES
        assert "de" in LANGUAGES
        for lang_code, meta in LANGUAGES.items():
            assert "name" in meta, f"Missing 'name' for {lang_code}"
            assert "flag" in meta, f"Missing 'flag' for {lang_code}"
