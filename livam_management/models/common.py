"""Shared helpers for the LiVaM management mirror.

Every ``livam_management`` model routes its LiVaM API calls through
:func:`get_client` so that credentials are read from ``ir.config_parameter``
(never from code or logs) and tests can patch a single seam.
"""

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.livam_connector.models.livam_client import (
    LivamApiError,
    get_livam_client,
)

__all__ = ["LivamApiError", "api_error", "get_client", "parse_dt"]


def get_client(env):
    """Return a configured LiVaM operator client (Bearer auth)."""
    return get_livam_client(env)


def api_error(exc):
    """Translate a LiVaM API failure into a user-facing error."""
    return UserError(_("LiVaM-Aufruf fehlgeschlagen: %s") % exc)


def parse_dt(value):
    """Normalise a LiVaM ISO-8601 datetime string into an Odoo Datetime value.

    LiVaM returns UTC ISO-8601 timestamps (e.g. ``2026-11-01T00:00:00.000Z``).
    Odoo's ``fields.Datetime`` parser expects the naive ``YYYY-MM-DD HH:MM:SS``
    form, so the timezone suffix and fractional seconds are dropped.
    """
    if not value:
        return False
    text = str(value).replace("T", " ", 1)
    if "." in text:
        text = text.split(".", 1)[0]
    text = text.replace("Z", "")
    if "+" in text:
        text = text.split("+", 1)[0]
    return text[:19]
