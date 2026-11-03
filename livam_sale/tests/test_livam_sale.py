from unittest import mock

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class FakeLivamClient:
    def __init__(self, create_order_response=None):
        self.create_order_response = create_order_response or {}
        self.create_order_calls = []
        self.operator_calls = []
        self.availability_calls = []
        self.availability_response = {"available": True}

    def create_order(self, payload):
        self.create_order_calls.append(payload)
        return self.create_order_response

    def check_tenant_availability(self, tenant_slug=None, domain=None):
        self.availability_calls.append((tenant_slug, domain))
        return self.availability_response

    def operator_request(self, method, path, payload=None):
        self.operator_calls.append((method, path, payload))
        return {}


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {"name": "Hans Praxis", "email": "hans@praxis.de"}
        )
        self.product = self.env["product.product"].create(
            {"name": "LiVaM SaaS Lizenz", "type": "service"}
        )

    def _order(self, **vals):
        vals.setdefault("partner_id", self.partner.id)
        vals.setdefault(
            "order_line",
            [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 1,
                        "price_unit": 49.0,
                    },
                )
            ],
        )
        return self.env["sale.order"].create(vals)

    def test_validate_identifier_rejects_both(self):
        order = self._order(
            livam_tenant_slug="hans", livam_domain="praxis-muster.de"
        )
        with self.assertRaises(UserError):
            order._livam_validate_identifier()

    def test_validate_identifier_rejects_neither(self):
        order = self._order()
        with self.assertRaises(UserError):
            order._livam_validate_identifier()

    def test_validate_identifier_accepts_slug(self):
        order = self._order(livam_tenant_slug="hans")
        order._livam_validate_identifier()

    def test_order_payload(self):
        order = self._order(
            livam_tenant_slug="hans",
            livam_billing_cycle="yearly",
            livam_features=" WEBSITE_BUILDER , BILLING ",
        )
        payload = order._livam_order_payload()
        self.assertEqual(payload["orderId"], order.name)
        self.assertEqual(payload["tenantSlug"], "hans")
        self.assertEqual(payload["billingCycle"], "yearly")
        self.assertFalse(payload["autoRenew"])
        self.assertEqual(payload["features"], ["WEBSITE_BUILDER", "BILLING"])
        self.assertEqual(payload["customerEmail"], "hans@praxis.de")
        self.assertIn("endsAt", payload)

    def test_provision_stores_license(self):
        fake = FakeLivamClient(
            create_order_response={
                "license": {"id": "lic_1", "provisioningStatus": "running"},
                "tenantUrl": "https://hans.lingavena.de",
            }
        )
        order = self._order(livam_tenant_slug="hans")
        with mock.patch(
            "odoo.addons.livam_sale.models.sale_order.get_livam_client",
            return_value=fake,
        ):
            order._livam_provision()
        self.assertEqual(order.livam_license_id, "lic_1")
        self.assertEqual(order.livam_tenant_url, "https://hans.lingavena.de")
        self.assertEqual(len(fake.create_order_calls), 1)

    def test_provision_skips_without_identifier(self):
        fake = FakeLivamClient()
        order = self._order()
        with mock.patch(
            "odoo.addons.livam_sale.models.sale_order.get_livam_client",
            return_value=fake,
        ):
            order._livam_provision()
        self.assertEqual(fake.create_order_calls, [])

    def test_check_availability(self):
        fake = FakeLivamClient()
        fake.availability_response = {"available": False, "reason": "taken"}
        order = self._order(livam_tenant_slug="hans")
        with mock.patch(
            "odoo.addons.livam_sale.models.sale_order.get_livam_client",
            return_value=fake,
        ):
            result = order._livam_check_availability()
        self.assertEqual(result, {"available": False, "reason": "taken"})
        self.assertEqual(fake.availability_calls, [("hans", None)])

    def test_apply_payment_first_then_renew(self):
        order = self._order(livam_tenant_slug="hans", livam_license_id="lic_1")
        fake = FakeLivamClient()
        with mock.patch(
            "odoo.addons.livam_sale.models.sale_order.get_livam_client",
            return_value=fake,
        ):
            order._livam_apply_payment()
            self.assertTrue(order.livam_marked_paid)
            order._livam_apply_payment()
        self.assertEqual(
            fake.operator_calls[0][:2], ("POST", "/licenses/lic_1/mark-paid")
        )
        self.assertEqual(
            fake.operator_calls[1][:2], ("POST", "/licenses/lic_1/renew")
        )
        self.assertEqual(fake.operator_calls[1][2], {"days": 30})


class TestAccountMove(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Hans Praxis"})

    def test_sync_skips_when_already_synced(self):
        move = self.env["account.move"].new(
            {"move_type": "out_invoice", "partner_id": self.partner.id,
             "livam_synced": True}
        )
        fake = FakeLivamClient()
        with mock.patch(
            "odoo.addons.livam_sale.models.account_move.get_livam_client",
            return_value=fake,
        ):
            move._livam_sync_payment_state()
        self.assertEqual(fake.operator_calls, [])

    def test_sync_skips_non_invoice(self):
        move = self.env["account.move"].new(
            {"move_type": "entry", "partner_id": self.partner.id}
        )
        fake = FakeLivamClient()
        with mock.patch(
            "odoo.addons.livam_sale.models.account_move.get_livam_client",
            return_value=fake,
        ):
            move._livam_sync_payment_state()
        self.assertEqual(fake.operator_calls, [])
