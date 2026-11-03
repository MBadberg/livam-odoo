from odoo.tests.common import TransactionCase

from odoo.addons.website_sale_livam.controllers.main import WebsiteSaleLivam


class TestWebsiteSaleLivam(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ctrl = WebsiteSaleLivam()

    def test_validate_rejects_both(self):
        self.assertTrue(self.ctrl._livam_validate_values("hans", "x.de"))

    def test_validate_rejects_neither(self):
        self.assertTrue(self.ctrl._livam_validate_values("", ""))

    def test_validate_rejects_bad_slug(self):
        self.assertTrue(self.ctrl._livam_validate_values("Bad Slug!", ""))

    def test_validate_rejects_bad_domain(self):
        self.assertTrue(self.ctrl._livam_validate_values("", "keine domain"))

    def test_validate_accepts_slug(self):
        self.assertIsNone(self.ctrl._livam_validate_values("hans", ""))

    def test_validate_accepts_domain(self):
        self.assertIsNone(
            self.ctrl._livam_validate_values("", "praxis-muster.de")
        )
