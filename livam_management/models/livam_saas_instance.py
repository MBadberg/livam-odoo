"""``livam.saas.instance`` — read-through mirror of a LiVaM SaaS instance."""

from odoo import fields, models

from . import common

INSTANCE_STATUSES = [
    ("active", "Aktiv"),
    ("maintenance", "Wartung"),
    ("decommissioned", "Außer Betrieb"),
]


class LivamSaaSInstance(models.Model):
    _name = "livam.saas.instance"
    _description = "LiVaM SaaS Instance"
    _order = "ref"

    name = fields.Char(string="Anzeigename", readonly=True)
    livam_id = fields.Char(string="LiVaM-ID", required=True, index=True, readonly=True)
    ref = fields.Char(string="Ref", readonly=True)
    base_url = fields.Char(string="Base URL", readonly=True)
    status = fields.Selection(INSTANCE_STATUSES, string="Status", readonly=True)
    capacity = fields.Integer(string="Kapazität", readonly=True)
    active_tenant_count = fields.Integer(string="Aktive Tenants", readonly=True)
    last_synced_at = fields.Datetime(string="Zuletzt synchronisiert", readonly=True)

    def _api_to_vals(self, data):
        return {
            "livam_id": data.get("id"),
            "name": data.get("displayName") or data.get("ref") or data.get("id"),
            "ref": data.get("ref"),
            "base_url": data.get("baseUrl"),
            "status": data.get("status"),
            "capacity": data.get("capacity") or 0,
            "active_tenant_count": data.get("activeTenantCount") or 0,
            "last_synced_at": fields.Datetime.now(),
        }

    def action_sync(self):
        client = common.get_client(self.env)
        try:
            data = client.operator_request("GET", "/saas-instances")
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        if not isinstance(data, list):
            data = []
        for item in data:
            vals = self._api_to_vals(item)
            existing = self.search([("livam_id", "=", item.get("id"))], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
        return True
