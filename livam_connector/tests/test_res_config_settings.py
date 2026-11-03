from odoo.tests.common import TransactionCase

from odoo.addons.livam_connector.models.livam_client import get_livam_client


class TestResConfigSettings(TransactionCase):
    def test_settings_roundtrip_via_config_parameter(self):
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("livam.base_url", "https://lus.example/")
        params.set_param("livam.operator_token", "op-token")
        params.set_param("livam.webhook_secret", "ws-secret")
        params.set_param("livam.timeout", "30")

        client = get_livam_client(self.env)
        self.assertEqual(client.base_url, "https://lus.example")
        self.assertEqual(client.operator_token, "op-token")
        self.assertEqual(client.webhook_secret, "ws-secret")
        self.assertEqual(client.timeout, 30)

    def test_defaults_when_unset(self):
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("livam.base_url", "")

        client = get_livam_client(self.env)
        self.assertEqual(client.base_url, "")
        self.assertEqual(client.timeout, 15)
