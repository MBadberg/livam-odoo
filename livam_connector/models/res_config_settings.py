from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    livam_base_url = fields.Char(
        string="LiVaM Base URL",
        config_parameter="livam.base_url",
        help="Basis-URL der LiVaM-Instanz, z.B. https://lus.lingavena.de",
    )
    livam_operator_token = fields.Char(
        string="Operator-Token",
        config_parameter="livam.operator_token",
    )
    livam_webhook_secret = fields.Char(
        string="Order-Webhook-Secret",
        config_parameter="livam.webhook_secret",
    )
    livam_timeout = fields.Integer(
        string="Timeout (Sekunden)",
        config_parameter="livam.timeout",
        default=15,
    )
