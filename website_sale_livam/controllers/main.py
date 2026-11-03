import logging
import re

from odoo import _, http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.addons.livam_connector.models.livam_client import (
    LivamApiError,
    get_livam_client,
)
from odoo.addons.livam_sale.models.sale_order import SLUG_RE

_logger = logging.getLogger(__name__)

DOMAIN_RE = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)


class WebsiteSaleLivam(WebsiteSale):

    def _livam_validate_values(self, tenant_slug, domain):
        """Return ``(error_key, message)`` or ``(None, None)``."""
        has_slug = bool(tenant_slug)
        has_domain = bool(domain)
        if has_slug == has_domain:
            return "livam_tenant_slug", _(
                "Bitte geben Sie entweder einen Tenant-Wunschnamen oder "
                "eine eigene Domain an."
            )
        if has_slug and not SLUG_RE.match(tenant_slug):
            return "livam_tenant_slug", _("Ungültiger Tenant-Wunschname.")
        if has_domain and not DOMAIN_RE.match(domain):
            return "livam_domain", _("Ungültige Domain.")
        return None, None

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super().checkout_form_validate(
            mode, all_form_values, data
        )
        tenant_slug = (
            all_form_values.get("livam_tenant_slug") or ""
        ).strip().lower()
        domain = (all_form_values.get("livam_domain") or "").strip().lower()
        key, message = self._livam_validate_values(tenant_slug, domain)
        if message:
            error[key] = "error"
            error_message.append(message)
            return error, error_message
        try:
            client = get_livam_client(request.env)
            result = client.check_tenant_availability(
                tenant_slug=tenant_slug or None,
                domain=domain or None,
            )
        except LivamApiError as exc:
            _logger.warning(
                "LiVaM-Verfügbarkeitsprüfung fehlgeschlagen: %s", exc
            )
            return error, error_message
        if not result.get("available"):
            error["livam_domain" if domain else "livam_tenant_slug"] = "error"
            error_message.append(_("Dieser Name ist bereits vergeben."))
        return error, error_message

    def _checkout_form_save(self, mode, checkout, all_values):
        res = super()._checkout_form_save(mode, checkout, all_values)
        tenant_slug = (
            all_values.get("livam_tenant_slug") or ""
        ).strip().lower()
        domain = (all_values.get("livam_domain") or "").strip().lower()
        billing_cycle = all_values.get("livam_billing_cycle")
        if billing_cycle not in ("monthly", "yearly"):
            billing_cycle = "monthly"
        checkout.write(
            {
                "livam_tenant_slug": tenant_slug,
                "livam_domain": domain,
                "livam_billing_cycle": billing_cycle,
            }
        )
        return res

    @http.route(
        "/shop/livam/check_availability",
        type="json",
        auth="public",
        website=True,
    )
    def livam_check_availability(self, tenant_slug=None, domain=None):
        tenant_slug = (tenant_slug or "").strip().lower()
        domain = (domain or "").strip().lower()
        key, message = self._livam_validate_values(tenant_slug, domain)
        if message:
            return {"available": False, "error": message}
        try:
            client = get_livam_client(request.env)
            return client.check_tenant_availability(
                tenant_slug=tenant_slug or None,
                domain=domain or None,
            )
        except LivamApiError as exc:
            return {"available": None, "error": str(exc)}
