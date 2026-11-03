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
        """Return an error message string, or ``None`` when valid.

        Messages are returned untranslated so the method stays a pure,
        testable helper; the HTTP routes translate where a request is active.
        """
        has_slug = bool(tenant_slug)
        has_domain = bool(domain)
        if has_slug == has_domain:
            return (
                "Bitte geben Sie entweder einen Tenant-Wunschnamen oder "
                "eine eigene Domain an."
            )
        if has_slug and not SLUG_RE.match(tenant_slug):
            return "Ungültiger Tenant-Wunschname."
        if has_domain and not DOMAIN_RE.match(domain):
            return "Ungültige Domain."
        return None

    def _livam_check_availability(self, tenant_slug, domain):
        """Return the LiVaM response dict, or ``None`` when unreachable."""
        try:
            client = get_livam_client(request.env)
            return client.check_tenant_availability(
                tenant_slug=tenant_slug or None,
                domain=domain or None,
            )
        except LivamApiError as exc:
            _logger.warning("LiVaM-Verfügbarkeitsprüfung fehlgeschlagen: %s", exc)
            return None

    @http.route(
        "/shop/livam_tenant",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def livam_tenant(self, **post):
        order_sudo = request.cart
        if redirection := self._check_cart(order_sudo):
            return redirection
        values = {
            "website_sale_order": order_sudo,
            "order": order_sudo,
            "error": None,
        }
        values.update(request.website._get_checkout_step_values())
        return request.render("website_sale_livam.livam_tenant", values)

    @http.route(
        "/shop/livam_tenant/save",
        type="http",
        methods=["POST"],
        auth="public",
        website=True,
        csrf=True,
        sitemap=False,
    )
    def livam_tenant_save(self, **post):
        order_sudo = request.cart
        if redirection := self._check_cart(order_sudo):
            return redirection
        tenant_slug = (post.get("livam_tenant_slug") or "").strip().lower()
        domain = (post.get("livam_domain") or "").strip().lower()
        billing_cycle = post.get("livam_billing_cycle")
        if billing_cycle not in ("monthly", "yearly"):
            billing_cycle = "monthly"

        error = self._livam_validate_values(tenant_slug, domain)
        if not error:
            result = self._livam_check_availability(tenant_slug, domain)
            if result is not None and not result.get("available"):
                error = _("Dieser Name ist bereits vergeben.")

        if error:
            values = {
                "website_sale_order": order_sudo,
                "order": order_sudo,
                "error": error,
            }
            values.update(request.website._get_checkout_step_values())
            return request.render("website_sale_livam.livam_tenant", values)

        order_sudo.write(
            {
                "livam_tenant_slug": tenant_slug,
                "livam_domain": domain,
                "livam_billing_cycle": billing_cycle,
            }
        )
        return request.redirect("/shop/payment")

    @http.route(
        "/shop/livam/check_availability",
        type="json",
        auth="public",
        website=True,
    )
    def livam_check_availability(self, tenant_slug=None, domain=None):
        tenant_slug = (tenant_slug or "").strip().lower()
        domain = (domain or "").strip().lower()
        error = self._livam_validate_values(tenant_slug, domain)
        if error:
            return {"available": False, "error": error}
        result = self._livam_check_availability(tenant_slug, domain)
        if result is None:
            return {"available": None, "error": _("LiVaM nicht erreichbar.")}
        return result
