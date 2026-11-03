from odoo.tests.common import TransactionCase

from odoo.addons.website_sale_livam.controllers.main import WebsiteSaleLivam


class TestWebsiteSaleLivam(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ctrl = WebsiteSaleLivam()

    def test_validate_rejects_both(self):
        key, message = self.ctrl._livam_validate_values("hans", "x.de")
        self.assertEqual(key, "livam_tenant_slug")
        self.assertTrue(message)

    def test_validate_rejects_neither(self):
        key, message = self.ctrl._livam_validate_values("", "")
        self.assertEqual(key, "livam_tenant_slug")
        self.assertTrue(message)

    def test_validate_rejects_bad_slug(self):
        key, message = self.ctrl._livam_validate_values("Bad Slug!", "")
        self.assertEqual(key, "livam_tenant_slug")
        self.assertTrue(message)

    def test_validate_rejects_bad_domain(self):
        key, message = self.ctrl._livam_validate_values("", "keine domain")
        self.assertEqual(key, "livam_domain")
        self.assertTrue(message)

    def test_validate_accepts_slug(self):
        key, message = self.ctrl._livam_validate_values("hans", "")
        self.assertIsNone(key)
        self.assertIsNone(message)

    def test_validate_accepts_domain(self):
        key, message = self.ctrl._livam_validate_values("", "praxis-muster.de")
        self.assertIsNone(key)
        self.assertIsNone(message)
