from odoo import fields, models


class LivamFeature(models.Model):
    _name = "livam.feature"
    _description = "LiVaM Feature Key"
    _order = "key"

    key = fields.Char(string="Key", required=True, index=True)
    name = fields.Char(string="Bezeichnung", required=True)

    _sql_constraints = [
        ("key_uniq", "unique(key)", "Feature-Keys müssen eindeutig sein."),
    ]
