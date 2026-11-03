from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    livam_license_id = fields.Char(string="LiVaM-Lizenz", copy=False)
    livam_tenant_slug = fields.Char(string="Tenant-Wunschname")
    livam_domain = fields.Char(string="Eigene Domain")
    livam_billing_cycle = fields.Selection(
        [("monthly", "Monatlich"), ("yearly", "Jährlich")],
        string="Abrechnungszyklus",
    )
