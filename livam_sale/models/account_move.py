import logging

from odoo import fields, models

from odoo.addons.livam_connector.models.livam_client import (
    LivamApiError,
    get_livam_client,
)

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    livam_synced = fields.Boolean(
        string="LiVaM-Zahlungssync erledigt",
        copy=False,
    )

    def _livam_linked_order(self):
        """Return the sale.order this invoice belongs to, if any."""
        self.ensure_one()
        orders = self.env["sale.order"].browse()
        for line in self.invoice_line_ids:
            orders |= line.sale_line_ids.order_id
        return orders[:1] if orders else None

    def _livam_sync_payment_state(self):
        """Idempotently sync paid invoices to LiVaM (mark-paid / renew).

        Safe to call repeatedly: each invoice is synced at most once
        (``livam_synced``), and failures leave the flag unset so the cron
        retries on the next run.
        """
        client = None
        for move in self:
            if move.livam_synced:
                continue
            if move.move_type != "out_invoice":
                continue
            if move.state != "posted" or move.payment_state != "paid":
                continue
            order = move._livam_linked_order()
            if not order or not order.livam_license_id:
                continue
            if client is None:
                client = get_livam_client(self.env)
            try:
                order._livam_apply_payment()
            except LivamApiError as exc:
                _logger.warning(
                    "LiVaM-Zahlungssync für %s fehlgeschlagen: %s",
                    move.name,
                    exc,
                )
                continue
            move.write({"livam_synced": True})

    def _livam_sync_payments_cron(self):
        moves = self.search(
            [
                ("livam_synced", "=", False),
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("payment_state", "=", "paid"),
            ]
        )
        moves._livam_sync_payment_state()
