import re
from datetime import datetime, timedelta, timezone

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.livam_connector.models.livam_client import (
    LivamApiError,
    get_livam_client,
)

SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    livam_license_id = fields.Char(
        string="LiVaM-Lizenz",
        readonly=True,
        copy=False,
        help="Lizenz-ID aus LiVaM, gesetzt beim Bestellabschluss.",
    )
    livam_tenant_slug = fields.Char(
        string="Tenant-Wunschname",
        help="Subdomain-Slug (z.B. 'hans' → hans.lingavena.de). "
        "Genau eines von Tenant-Wunschname / eigene Domain.",
    )
    livam_domain = fields.Char(
        string="Eigene Domain",
        help="Kundeneigene Domain (z.B. praxis-muster.de). "
        "Genau eines von Tenant-Wunschname / eigene Domain.",
    )
    livam_billing_cycle = fields.Selection(
        [("monthly", "Monatlich"), ("yearly", "Jährlich")],
        string="Abrechnungszyklus",
        default="monthly",
        required=True,
    )
    livam_features = fields.Char(
        string="Feature-Keys",
        help="Komma-getrennte Lingavena-Feature-Keys "
        "(z.B. WEBSITE_BUILDER,BILLING).",
    )
    livam_tenant_url = fields.Char(string="Tenant-URL", readonly=True, copy=False)
    livam_provisioning_status = fields.Char(
        string="Provisioning-Status", readonly=True, copy=False
    )
    livam_marked_paid = fields.Boolean(string="Erstzahlung bestätigt", copy=False)

    # -- helper ------------------------------------------------------------

    def _livam_feature_list(self):
        self.ensure_one()
        if not self.livam_features:
            return []
        return [key.strip() for key in self.livam_features.split(",") if key.strip()]

    def _livam_ends_at(self):
        self.ensure_one()
        days = 365 if self.livam_billing_cycle == "yearly" else 30
        end = datetime.now(timezone.utc) + timedelta(days=days)
        return end.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _livam_validate_identifier(self):
        self.ensure_one()
        has_slug = bool(self.livam_tenant_slug)
        has_domain = bool(self.livam_domain)
        if has_slug == has_domain:
            raise UserError(
                _(
                    "Geben Sie entweder einen Tenant-Wunschnamen oder eine "
                    "eigene Domain an (genau eines)."
                )
            )
        if has_slug and not SLUG_RE.match(self.livam_tenant_slug.strip()):
            raise UserError(
                _("Ungültiger Tenant-Wunschname '%s'.") % self.livam_tenant_slug.strip()
            )

    def _livam_order_payload(self):
        self.ensure_one()
        self._livam_validate_identifier()
        payload = {
            "orderId": self.name,
            "licenseType": "subscription",
            "maxInstances": 1,
            "autoRenew": False,
            "billingCycle": self.livam_billing_cycle,
            "customerEmail": self.partner_id.email or None,
            "customerName": self.partner_id.name or None,
            "endsAt": self._livam_ends_at(),
        }
        if self.livam_tenant_slug:
            payload["tenantSlug"] = self.livam_tenant_slug.strip()
        if self.livam_domain:
            payload["domain"] = self.livam_domain.strip()
        features = self._livam_feature_list()
        if features:
            payload["features"] = features
        return payload

    def _livam_check_availability(self):
        """Check tenant slug/domain availability via LiVaM.

        Returns the LiVaM response dict (e.g. ``{"available": True}``); a
        taken identity is a normal result, not an error.
        """
        self.ensure_one()
        self._livam_validate_identifier()
        client = get_livam_client(self.env)
        return client.check_tenant_availability(
            tenant_slug=(self.livam_tenant_slug or "").strip() or None,
            domain=(self.livam_domain or "").strip() or None,
        )

    # -- provisioning ------------------------------------------------------

    def _livam_provision(self):
        client = None
        for order in self:
            if order.livam_license_id:
                continue
            if not order.livam_tenant_slug and not order.livam_domain:
                continue  # kein LiVaM-Lizenz-Auftrag
            if client is None:
                client = get_livam_client(self.env)
            try:
                result = client.create_order(order._livam_order_payload())
            except LivamApiError as exc:
                raise UserError(
                    _("LiVaM-Provisionierung fehlgeschlagen: %s") % exc
                ) from exc
            order._livam_store_provisioning_result(result)
            order._livam_create_contract()

    def _livam_store_provisioning_result(self, result):
        self.ensure_one()
        license_data = (result or {}).get("license") or {}
        self.write(
            {
                "livam_license_id": license_data.get("id"),
                "livam_tenant_url": (result or {}).get("tenantUrl"),
                "livam_provisioning_status": license_data.get("provisioningStatus"),
            }
        )

    def _livam_create_contract(self):
        self.ensure_one()
        contract_model = self.env.get("contract.contract")
        if not contract_model:
            return False
        recurring = "yearly" if self.livam_billing_cycle == "yearly" else "monthly"
        line_vals = []
        for line in self.order_line.filtered(
            lambda order_line: not order_line.display_type
        ):
            line_vals.append(
                (
                    0,
                    0,
                    {
                        "name": line.name,
                        "product_id": line.product_id.id,
                        "quantity": line.product_uom_qty,
                        "price_unit": line.price_unit,
                        "uom_id": line.product_uom.id,
                    },
                )
            )
        return contract_model.create(
            {
                "name": self.name,
                "partner_id": self.partner_id.id,
                "date_start": fields.Date.context_today(self),
                "recurring_rule_type": recurring,
                "recurring_interval": 1,
                "livam_license_id": self.livam_license_id,
                "livam_tenant_slug": self.livam_tenant_slug,
                "livam_domain": self.livam_domain,
                "livam_billing_cycle": self.livam_billing_cycle,
                "contract_line_ids": line_vals,
            }
        )

    # -- payment sync ------------------------------------------------------

    def _livam_apply_payment(self):
        """Mark-paid (first) or renew (subsequent) for this order's license."""
        self.ensure_one()
        if not self.livam_license_id:
            return
        client = get_livam_client(self.env)
        if not self.livam_marked_paid:
            client.operator_request(
                "POST", "/licenses/%s/mark-paid" % self.livam_license_id
            )
            self.write({"livam_marked_paid": True})
        else:
            days = 365 if self.livam_billing_cycle == "yearly" else 30
            client.operator_request(
                "POST",
                "/licenses/%s/renew" % self.livam_license_id,
                {"days": days},
            )

    # -- confirm hook ------------------------------------------------------

    def action_confirm(self):
        res = super().action_confirm()
        self._livam_provision()
        return res
