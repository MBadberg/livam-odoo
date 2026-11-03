"""Transient models for parameterised LiVaM management actions."""

from odoo import fields, models

from . import common
from .livam_license import LICENSE_TYPES

INSTANCE_STATUSES = [
    ("active", "Aktiv"),
    ("maintenance", "Wartung"),
    ("decommissioned", "Außer Betrieb"),
]


class LivamLicenseFeaturesWizard(models.TransientModel):
    _name = "livam.license.features.wizard"
    _description = "LiVaM License Features"

    license_id = fields.Many2one("livam.license", required=True, ondelete="cascade")
    feature_ids = fields.Many2many("livam.feature", string="Feature-Keys")

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        license_id = self.env.context.get("active_id")
        if license_id:
            license_rec = self.env["livam.license"].browse(license_id)
            keys = [
                key.strip()
                for key in (license_rec.features or "").split(",")
                if key.strip()
            ]
            features = self.env["livam.feature"].search([("key", "in", keys)])
            res.update(
                {
                    "license_id": license_id,
                    "feature_ids": [(6, 0, features.ids)],
                }
            )
        return res

    def action_apply(self):
        self.ensure_one()
        self.license_id._set_features(sorted(self.feature_ids.mapped("key")))
        return {"type": "ir.actions.act_window_close"}


class LivamMoveLicenseWizard(models.TransientModel):
    _name = "livam.move.license.wizard"
    _description = "Move LiVaM License to another SaaS Instance"

    license_id = fields.Many2one("livam.license", required=True, ondelete="cascade")
    target_instance_id = fields.Many2one(
        "livam.saas.instance",
        string="Ziel-Instanz",
        required=True,
        domain=[("status", "=", "active")],
    )

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        license_id = self.env.context.get("active_id")
        if license_id:
            res["license_id"] = license_id
        return res

    def action_move(self):
        self.ensure_one()
        self.license_id._move(self.target_instance_id)
        return {"type": "ir.actions.act_window_close"}


class LivamSaaSInstanceWizard(models.TransientModel):
    _name = "livam.saas.instance.wizard"
    _description = "Register LiVaM SaaS Instance"

    name = fields.Char(string="Anzeigename", required=True)
    ref = fields.Char(string="Ref", required=True)
    base_url = fields.Char(string="Base URL", required=True)
    capacity = fields.Integer(string="Kapazität", default=0)
    status = fields.Selection(INSTANCE_STATUSES, string="Status", default="active")

    def action_register(self):
        self.ensure_one()
        client = common.get_client(self.env)
        try:
            client.operator_request(
                "POST",
                "/saas-instances",
                {
                    "ref": self.ref,
                    "displayName": self.name,
                    "baseUrl": self.base_url,
                    "capacity": self.capacity,
                    "status": self.status,
                },
            )
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        self.env["livam.saas.instance"].action_sync()
        return {"type": "ir.actions.act_window_close"}


class LivamLicenseCreateWizard(models.TransientModel):
    _name = "livam.license.create.wizard"
    _description = "Create LiVaM License"

    license_type = fields.Selection(
        LICENSE_TYPES, string="Lizenztyp", required=True, default="subscription"
    )
    max_instances = fields.Integer(string="Max. Instanzen", default=1)
    feature_ids = fields.Many2many("livam.feature", string="Feature-Keys")
    auto_renew = fields.Boolean(string="Auto-Renew", default=False)
    ends_at = fields.Datetime(string="Ende")
    license_key = fields.Char(string="Lizenzschlüssel")

    def action_create(self):
        self.ensure_one()
        payload = {
            "licenseType": self.license_type,
            "maxInstances": self.max_instances,
            "features": sorted(self.feature_ids.mapped("key")),
            "autoRenew": self.auto_renew,
        }
        if self.ends_at:
            payload["endsAt"] = self.ends_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        if self.license_key:
            payload["licenseKey"] = self.license_key
        client = common.get_client(self.env)
        try:
            client.operator_request("POST", "/licenses", payload)
        except common.LivamApiError as exc:
            raise common.api_error(exc) from exc
        self.env["livam.license"].action_sync()
        return {"type": "ir.actions.act_window_close"}

