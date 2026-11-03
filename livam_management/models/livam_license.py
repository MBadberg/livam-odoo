"""``livam.license`` — read-through mirror of a LiVaM license.

The record mirrors the LiVaM operator view (``GET /licenses``). Write actions
(mark-paid, renew, suspend, activate, features, move) call the operator API and
then re-sync this single record.
"""

from odoo import fields, models

from . import common

LICENSE_TYPES = [
    ("trial", "Trial"),
    ("subscription", "Abonnement"),
    ("perpetual", "Perpetual"),
]
LICENSE_STATUSES = [
    ("active", "Aktiv"),
    ("suspended", "Suspendiert"),
    ("expired", "Abgelaufen"),
    ("cancelled", "Gekündigt"),
]
PAYMENT_STATUSES = [
    ("unpaid", "Unbezahlt"),
    ("paid", "Bezahlt"),
    ("refunded", "Erstattet"),
    ("cancelled", "Storniert"),
]
RENEWAL_STATUSES = [
    ("ok", "OK"),
    ("needs_review", "Prüfung nötig"),
]
PROVISIONING_STATUSES = [
    ("none", "Keine"),
    ("pending", "Ausstehend"),
    ("provisioning", "In Provisionierung"),
    ("running", "Läuft"),
    ("suspended", "Suspendiert"),
    ("decommissioned", "Außer Betrieb"),
    ("failed", "Fehlgeschlagen"),
]
TENANT_RUNTIME_STATUSES = [
    ("provisioning", "In Provisionierung"),
    ("running", "Läuft"),
    ("isolated", "Isoliert"),
    ("suspended", "Suspendiert"),
    ("decommissioned", "Außer Betrieb"),
]
BILLING_CYCLES = [
    ("monthly", "Monatlich"),
    ("yearly", "Jährlich"),
]


class LivamLicense(models.Model):
    _name = "livam.license"
    _description = "LiVaM License"
    _order = "name"

    name = fields.Char(string="Bezeichnung", readonly=True)
    livam_id = fields.Char(string="LiVaM-ID", required=True, index=True, readonly=True)
    license_key = fields.Char(string="Lizenzschlüssel", readonly=True)
    license_type = fields.Selection(LICENSE_TYPES, string="Lizenztyp", readonly=True)
    status = fields.Selection(LICENSE_STATUSES, string="Status", readonly=True)
    payment_status = fields.Selection(
        PAYMENT_STATUSES, string="Zahlungsstatus", readonly=True
    )
    auto_renew = fields.Boolean(string="Auto-Renew", readonly=True)
    renewal_status = fields.Selection(
        RENEWAL_STATUSES, string="Renewal-Status", readonly=True
    )
    max_instances = fields.Integer(string="Max. Instanzen", readonly=True)
    features = fields.Char(string="Feature-Keys", readonly=True)
    tenant_ref = fields.Char(string="Tenant-Ref", readonly=True)
    domain = fields.Char(string="Domain", readonly=True)
    customer_email = fields.Char(string="Kunden-E-Mail", readonly=True)
    customer_name = fields.Char(string="Kundenname", readonly=True)
    billing_cycle = fields.Selection(
        BILLING_CYCLES, string="Abrechnungszyklus", readonly=True
    )
    provisioning_status = fields.Selection(
        PROVISIONING_STATUSES, string="Provisioning-Status", readonly=True
    )
    tenant_runtime_status = fields.Selection(
        TENANT_RUNTIME_STATUSES, string="Tenant-Runtime-Status", readonly=True
    )
    saas_instance_ref = fields.Char(string="SaaS-Instanz-Ref", readonly=True)
    saas_instance_id = fields.Many2one(
        "livam.saas.instance", string="SaaS-Instanz", readonly=True
    )
    partner_id = fields.Many2one("res.partner", string="Kunde", index=True)
    starts_at = fields.Datetime(string="Beginn", readonly=True)
    ends_at = fields.Datetime(string="Ende", readonly=True)
    installation_count = fields.Integer(string="Installationen", readonly=True)
    highlight = fields.Char(string="Hinweis", readonly=True)
    transition = fields.Char(string="Geplanter Übergang", readonly=True)
    last_synced_at = fields.Datetime(string="Zuletzt synchronisiert", readonly=True)

    # -- mapping ------------------------------------------------------------

    def _api_to_vals(self, data):
        vals = {
            "livam_id": data.get("id"),
            "name": data.get("tenantRef") or data.get("licenseKey") or data.get("id"),
            "license_key": data.get("licenseKey"),
            "license_type": data.get("licenseType"),
            "status": data.get("status"),
            "payment_status": data.get("paymentStatus"),
            "auto_renew": bool(data.get("autoRenew")),
            "renewal_status": data.get("renewalStatus"),
            "max_instances": data.get("maxInstances") or 0,
            "features": ", ".join(sorted(data.get("features") or [])),
            "tenant_ref": data.get("tenantRef"),
            "domain": data.get("domain"),
            "customer_email": data.get("customerEmail"),
            "customer_name": data.get("customerName"),
            "billing_cycle": data.get("billingCycle"),
            "provisioning_status": data.get("provisioningStatus"),
            "tenant_runtime_status": data.get("tenantRuntimeStatus"),
            "saas_instance_ref": data.get("saasInstanceRef"),
            "starts_at": common.parse_dt(data.get("startsAt")),
            "ends_at": common.parse_dt(data.get("endsAt")),
            "installation_count": data.get("installationCount") or 0,
            "highlight": data.get("highlight"),
            "transition": data.get("transition"),
            "last_synced_at": fields.Datetime.now(),
        }
        instance_id = self._resolve_saas_instance(data.get("saasInstanceId"))
        if instance_id:
            vals["saas_instance_id"] = instance_id
        return vals

    def _resolve_saas_instance(self, livam_id):
        if not livam_id:
            return False
        instance = self.env["livam.saas.instance"].search(
            [("livam_id", "=", livam_id)], limit=1
        )
        return instance.id if instance else False

    def _resolve_partner(self, data):
        email = (data.get("customerEmail") or "").strip()
        name = (data.get("customerName") or "").strip()
        if email:
            partner = self.env["res.partner"].search([("email", "=", email)], limit=1)
            if partner:
                return partner.id
        if name:
            partner = self.env["res.partner"].search([("name", "=", name)], limit=1)
            if partner:
                return partner.id
        return False

    # -- sync ---------------------------------------------------------------

    def action_sync(self):
        client = common.get_client(self.env)
        try:
            data = client.operator_request("GET", "/licenses")
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        if not isinstance(data, list):
            data = []
        for item in data:
            vals = self._api_to_vals(item)
            existing = self.search([("livam_id", "=", item.get("id"))], limit=1)
            if existing:
                if not existing.partner_id:
                    vals["partner_id"] = self._resolve_partner(item)
                existing.write(vals)
            else:
                vals["partner_id"] = self._resolve_partner(item)
                self.create(vals)
        return True

    def action_sync_one(self):
        self.ensure_one()
        client = common.get_client(self.env)
        try:
            data = client.operator_request("GET", "/licenses/%s" % self.livam_id)
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        vals = self._api_to_vals(data)
        if not self.partner_id:
            vals["partner_id"] = self._resolve_partner(data)
        self.write(vals)
        return True

    def action_sync_all(self):
        self.env["livam.saas.instance"].action_sync()
        self.env["livam.license"].action_sync()
        self.env["livam.installation"].action_sync()
        self.env["livam.release"].action_sync()
        return True

    # -- write actions ------------------------------------------------------

    def _operator_post(self, path, payload=None):
        client = common.get_client(self.env)
        try:
            return client.operator_request("POST", path, payload)
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc

    def action_mark_paid(self):
        self.ensure_one()
        self._operator_post("/licenses/%s/mark-paid" % self.livam_id)
        return self.action_sync_one()

    def action_renew(self):
        self.ensure_one()
        days = 365 if self.billing_cycle == "yearly" else 30
        self._operator_post("/licenses/%s/renew" % self.livam_id, {"days": days})
        return self.action_sync_one()

    def action_suspend(self):
        self.ensure_one()
        self._operator_post("/licenses/%s/suspend" % self.livam_id)
        return self.action_sync_one()

    def action_activate(self):
        self.ensure_one()
        self._operator_post("/licenses/%s/activate" % self.livam_id)
        return self.action_sync_one()

    def _set_features(self, keys):
        self.ensure_one()
        self._operator_post(
            "/licenses/%s/features" % self.livam_id, {"features": list(keys)}
        )
        return self.action_sync_one()

    def _move(self, target_instance):
        self.ensure_one()
        self._operator_post(
            "/licenses/%s/move" % self.livam_id,
            {"saasInstanceRef": target_instance.ref},
        )
        return self.action_sync_one()

