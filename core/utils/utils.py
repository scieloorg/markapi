import logging

from django.contrib.auth import get_user_model

from langcodes import Language

from core.utils.requester import NonRetryableError, fetch_data


logger = logging.getLogger(__name__)

__all__ = [
    "fetch_data",
    "language_iso",
    "NonRetryableError",
    "_get_user",
]


def language_iso(code):
    """Normalize a language code to its shortest ISO 639 form.

    Uses the ``langcodes`` library to parse ``code`` and return the two-letter
    language subtag when valid (e.g. ``"pt-BR"`` → ``"pt"``).

    Returns an empty string when the code is ``None``, empty or cannot be
    parsed into a valid language.
    """
    if not code:
        return ""
    try:
        lang = Language.get(code)
        if lang.is_valid():
            return lang.language or ""
    except Exception:
        pass
    return ""


def _get_user(request, username=None, user_id=None):
    """Resolve the acting user from the current request context.

    Attempts to look up the user by ``request.user_id`` first.  If that
    attribute is missing (``AttributeError``), falls back to ``user_id``
    or ``username``.
    """
    User = get_user_model()
    try:
        return User.objects.get(pk=request.user_id)
    except AttributeError:
        if user_id:
            return User.objects.get(pk=user_id)
        if username:
            return User.objects.get(username=username)
