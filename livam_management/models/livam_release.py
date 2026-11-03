"""``livam.release`` — read-through mirror of a LiVaM release."""

from odoo import fields, models

from . import common

CHANNELS = [
    ("stable", "Stable"),
    ("beta", "Beta"),
]


class LivamRelease(models.Model):
    _name = "livam.release"
    _description = "LiVaM Release"
    _order = "released_at desc"

    name = fields.Char(string="Bezeichnung", readonly=True)
    livam_id = fields.Char(string="LiVaM-ID", required=True, index=True, readonly=True)
    channel = fields.Selection(CHANNELS, string="Kanal", readonly=True)
    version = fields.Char(string="Version", readonly=True)
    image_name = fields.Char(string="Image", readonly=True)
    image_digest = fields.Char(string="Image-Digest", readonly=True)
    sbom_checksum = fields.Char(string="SBOM-Checksumme", readonly=True)
    enabled = fields.Boolean(string="Aktiviert", readonly=True)
    released_at = fields.Datetime(string="Veröffentlicht", readonly=True)
    last_synced_at = fields.Datetime(string="Zuletzt synchronisiert", readonly=True)

    def _api_to_vals(self, data):
        channel = data.get("channel") or ""
        version = data.get("version") or ""
        return {
            "livam_id": data.get("id"),
            "name": ("%s %s" % (channel, version)).strip() or data.get("id"),
            "channel": channel or False,
            "version": version,
            "image_name": data.get("imageName"),
            "image_digest": data.get("imageDigest"),
            "sbom_checksum": data.get("sbomChecksum"),
            "enabled": bool(data.get("enabled")),
            "released_at": common.parse_dt(data.get("releasedAt")),
            "last_synced_at": fields.Datetime.now(),
        }

    def action_sync(self):
        client = common.get_client(self.env)
        try:
            data = client.operator_request("GET", "/releases")
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

    def _set_enabled(self, enabled):
        self.ensure_one()
        action = "activate" if enabled else "deactivate"
        client = common.get_client(self.env)
        try:
            data = client.operator_request(
                "POST", "/releases/%s/%s" % (self.livam_id, action)
            )
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        if isinstance(data, dict) and data.get("id"):
            self.write(self._api_to_vals(data))
        return True

    def action_activate(self):
        return self._set_enabled(True)

    def action_deactivate(self):
        return self._set_enabled(False)
