"""``livam.installation`` — read-through mirror of a LiVaM installation."""

from odoo import fields, models

from . import common

DEPLOYMENT_MODES = [
    ("self_hosted", "Self-hosted"),
    ("saas", "SaaS"),
]


class LivamInstallation(models.Model):
    _name = "livam.installation"
    _description = "LiVaM Installation"
    _order = "name"

    name = fields.Char(string="Bezeichnung", readonly=True)
    livam_id = fields.Char(string="LiVaM-ID", required=True, index=True, readonly=True)
    installation_uuid = fields.Char(string="Installations-UUID", readonly=True)
    license_id = fields.Many2one("livam.license", string="Lizenz", readonly=True)
    instance_key = fields.Char(string="Instanz-Schlüssel", readonly=True)
    deployment_mode = fields.Selection(
        DEPLOYMENT_MODES, string="Deployment-Modus", readonly=True
    )
    server_url = fields.Char(string="Server-URL", readonly=True)
    software_version = fields.Char(string="Software-Version", readonly=True)
    online = fields.Boolean(string="Online", readonly=True)
    first_seen_at = fields.Datetime(string="Zuerst gesehen", readonly=True)
    last_seen_at = fields.Datetime(string="Zuletzt gesehen", readonly=True)
    last_synced_at = fields.Datetime(string="Zuletzt synchronisiert", readonly=True)

    def _api_to_vals(self, data):
        return {
            "livam_id": data.get("id"),
            "name": data.get("installationUuid")
            or data.get("instanceKey")
            or data.get("id"),
            "installation_uuid": data.get("installationUuid"),
            "instance_key": data.get("instanceKey"),
            "deployment_mode": data.get("deploymentMode"),
            "server_url": data.get("serverUrl"),
            "software_version": data.get("softwareVersion"),
            "first_seen_at": common.parse_dt(data.get("firstSeenAt")),
            "last_seen_at": common.parse_dt(data.get("lastSeenAt")),
            "last_synced_at": fields.Datetime.now(),
        }

    def _resolve_license(self, livam_id):
        if not livam_id:
            return False
        license_rec = self.env["livam.license"].search(
            [("livam_id", "=", livam_id)], limit=1
        )
        return license_rec.id if license_rec else False

    def action_sync(self):
        client = common.get_client(self.env)
        try:
            data = client.operator_request("GET", "/installations")
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        if not isinstance(data, list):
            data = []
        for item in data:
            inst = item.get("installation") or {}
            vals = self._api_to_vals(inst)
            vals["online"] = bool(item.get("online"))
            vals["license_id"] = self._resolve_license(
                (item.get("license") or {}).get("id")
            )
            existing = self.search([("livam_id", "=", inst.get("id"))], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
        return True

    def action_sync_one(self):
        self.ensure_one()
        client = common.get_client(self.env)
        try:
            data = client.operator_request("GET", "/installations/%s" % self.livam_id)
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        inst = data.get("installation") or {}
        vals = self._api_to_vals(inst)
        vals["online"] = bool(data.get("online"))
        vals["license_id"] = self._resolve_license(
            (data.get("license") or {}).get("id")
        )
        self.write(vals)
        return True

    def action_revoke_certificate(self):
        self.ensure_one()
        client = common.get_client(self.env)
        try:
            client.operator_request(
                "POST", "/installations/%s/revoke-certificate" % self.livam_id
            )
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        return self.action_sync_one()
