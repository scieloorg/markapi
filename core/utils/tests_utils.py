from unittest import TestCase
from unittest.mock import MagicMock, patch

from langcodes import Language

from core.utils.utils import _get_user, language_iso


class LanguageIsoTests(TestCase):
    """Tests for the ``language_iso`` helper."""

    def test_normalises_pt_br(self):
        self.assertEqual(language_iso("pt-BR"), "pt")

    def test_normalises_en_us(self):
        self.assertEqual(language_iso("en-US"), "en")

    def test_normalises_es_419(self):
        self.assertEqual(language_iso("es-419"), "es")

    def test_simple_code_unchanged(self):
        self.assertEqual(language_iso("fr"), "fr")

    def test_empty_string_returns_empty(self):
        self.assertEqual(language_iso(""), "")

    def test_none_returns_empty(self):
        self.assertEqual(language_iso(None), "")

    def test_invalid_code_returns_empty(self):
        self.assertEqual(language_iso("zzzzzz"), "")


class GetUserTests(TestCase):
    """Tests for the ``_get_user`` helper."""

    @patch("core.utils.utils.get_user_model")
    def test_resolves_by_request_user_id(self, mock_get_user_model):
        mock_user_model = MagicMock()
        mock_get_user_model.return_value = mock_user_model
        request = MagicMock()
        request.user_id = 42
        sentinel = object()
        mock_user_model.objects.get.return_value = sentinel

        result = _get_user(request)

        mock_user_model.objects.get.assert_called_once_with(pk=42)
        self.assertIs(result, sentinel)

    @patch("core.utils.utils.get_user_model")
    def test_falls_back_to_user_id(self, mock_get_user_model):
        mock_user_model = MagicMock()
        mock_get_user_model.return_value = mock_user_model
        request = MagicMock(spec=[])  # no user_id attribute
        sentinel = object()
        mock_user_model.objects.get.return_value = sentinel

        result = _get_user(request, user_id=7)

        mock_user_model.objects.get.assert_called_once_with(pk=7)
        self.assertIs(result, sentinel)

    @patch("core.utils.utils.get_user_model")
    def test_falls_back_to_username(self, mock_get_user_model):
        mock_user_model = MagicMock()
        mock_get_user_model.return_value = mock_user_model
        request = MagicMock(spec=[])  # no user_id attribute
        sentinel = object()
        mock_user_model.objects.get.return_value = sentinel

        result = _get_user(request, username="alice")

        mock_user_model.objects.get.assert_called_once_with(username="alice")
        self.assertIs(result, sentinel)

    @patch("core.utils.utils.get_user_model")
    def test_user_id_preferred_over_username(self, mock_get_user_model):
        mock_user_model = MagicMock()
        mock_get_user_model.return_value = mock_user_model
        request = MagicMock(spec=[])  # no user_id attribute
        sentinel = object()
        mock_user_model.objects.get.return_value = sentinel

        result = _get_user(request, username="alice", user_id=7)

        mock_user_model.objects.get.assert_called_once_with(pk=7)
        self.assertIs(result, sentinel)
