from unittest import mock

from odoo.tests.common import TransactionCase


class FakeLivamClient:
    """Records operator calls and returns canned responses."""

    def __init__(self):
        self.calls = []
        self.licenses = []
        self.installations = []
        self.releases = []
        self.saas_instances = []
        self.license_single = None
        self.installation_single = None

    def operator_request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET" and path == "/licenses":
            return self.licenses
        if method == "GET" and path.startswith("/licenses/"):
            return self.license_single or {}
        if method == "GET" and path == "/installations":
            return self.installations
        if method == "GET" and path.startswith("/installations/"):
            return self.installation_single or {}
        if method == "GET" and path == "/releases":
            return self.releases
        if method == "GET" and path == "/saas-instances":
            return self.saas_instances
        return {}


def license_dict(livam_id="lic_1", **overrides):
    data = {
        "id": livam_id,
        "licenseKey": "LING-ABC",
        "licenseType": "subscription",
        "status": "active",
        "paymentStatus": "unpaid",
        "autoRenew": False,
        "renewalStatus": "ok",
        "maxInstances": 1,
        "features": ["WEBSITE_BUILDER", "BILLING"],
        "tenantRef": "hans",
        "domain": None,
        "customerEmail": "hans@praxis.de",
        "customerName": "Hans Praxis",
        "billingCycle": "monthly",
        "provisioningStatus": "running",
        "tenantRuntimeStatus": "running",
        "saasInstanceRef": "inst_1",
        "saasInstanceId": "si_1",
        "startsAt": "2026-11-01T00:00:00.000Z",
        "endsAt": "2026-12-01T00:00:00.000Z",
        "installationCount": 0,
        "highlight": None,
        "transition": None,
    }
    data.update(overrides)
    return data


def instance_dict(livam_id="si_1", **overrides):
    data = {
        "id": livam_id,
        "ref": "inst_1",
        "displayName": "EU-West",
        "baseUrl": "https://saas.example",
        "status": "active",
        "capacity": 10,
        "activeTenantCount": 3,
    }
    data.update(overrides)
    return data


def release_dict(livam_id="rel_1", **overrides):
    data = {
        "id": livam_id,
        "channel": "beta",
        "version": "1.4.0",
        "imageName": "lingavena",
        "imageDigest": "sha256:abc",
        "sbomChecksum": "sha256:def",
        "enabled": True,
        "releasedAt": "2026-11-01T00:00:00.000Z",
    }
    data.update(overrides)
    return data


def installation_item(installation_id="inst_9", license_id="lic_1"):
    return {
        "installation": {
            "id": installation_id,
            "installationUuid": "uuid-1",
            "instanceKey": "ABCDEF",
            "deploymentMode": "self_hosted",
            "serverUrl": "https://x.example",
            "softwareVersion": "1.4.0",
            "firstSeenAt": "2026-10-01T00:00:00.000Z",
            "lastSeenAt": "2026-11-01T00:00:00.000Z",
        },
        "license": license_dict(license_id) if license_id else None,
        "online": True,
        "instances": [],
    }


class TestLivamManagement(TransactionCase):
    def setUp(self):
        super().setUp()
        self.fake = FakeLivamClient()
        patcher = mock.patch(
            "odoo.addons.livam_management.models.common.get_livam_client",
            return_value=self.fake,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    # -- license mirror -----------------------------------------------------

    def test_sync_licenses_creates_records(self):
        self.fake.licenses = [
            license_dict("lic_1"),
            license_dict(
                "lic_2",
                tenantRef="klara",
                customerEmail="klara@praxis.de",
                customerName="Klara Logopädie",
            ),
        ]
        self.env["livam.license"].action_sync()
        licenses = self.env["livam.license"].search([])
        self.assertEqual(len(licenses), 2)
        lic = self.env["livam.license"].search([("livam_id", "=", "lic_1")])
        self.assertEqual(lic.name, "hans")
        self.assertEqual(lic.status, "active")
        self.assertEqual(lic.features, "BILLING, WEBSITE_BUILDER")
        self.assertEqual(lic.installation_count, 0)

    def test_sync_licenses_is_idempotent(self):
        self.fake.licenses = [license_dict("lic_1")]
        self.env["livam.license"].action_sync()
        self.env["livam.license"].action_sync()
        self.assertEqual(
            self.env["livam.license"].search_count([("livam_id", "=", "lic_1")]), 1
        )

    def test_sync_licenses_assigns_partner_by_email(self):
        partner = self.env["res.partner"].create(
            {"name": "Hans Praxis", "email": "hans@praxis.de"}
        )
        self.fake.licenses = [license_dict("lic_1")]
        self.env["livam.license"].action_sync()
        lic = self.env["livam.license"].search([("livam_id", "=", "lic_1")])
        self.assertEqual(lic.partner_id, partner)

    def test_sync_licenses_keeps_manual_partner(self):
        partner = self.env["res.partner"].create({"name": "Manuell zugeordnet"})
        lic = self.env["livam.license"].create({"livam_id": "lic_1", "name": "hans"})
        lic.partner_id = partner
        self.fake.licenses = [license_dict("lic_1")]
        self.env["livam.license"].action_sync()
        self.assertEqual(lic.partner_id, partner)

    def test_sync_licenses_resolves_saas_instance(self):
        self.fake.saas_instances = [instance_dict("si_1")]
        self.env["livam.saas.instance"].action_sync()
        self.fake.licenses = [license_dict("lic_1")]
        self.env["livam.license"].action_sync()
        lic = self.env["livam.license"].search([("livam_id", "=", "lic_1")])
        self.assertEqual(lic.saas_instance_id.ref, "inst_1")

    # -- other mirrors ------------------------------------------------------

    def test_sync_installations_maps_nested_shape(self):
        self.fake.licenses = [license_dict("lic_1")]
        self.env["livam.license"].action_sync()
        self.fake.installations = [installation_item("inst_9", "lic_1")]
        self.env["livam.installation"].action_sync()
        inst = self.env["livam.installation"].search([("livam_id", "=", "inst_9")])
        self.assertTrue(inst.online)
        self.assertEqual(inst.license_id.livam_id, "lic_1")

    def test_sync_releases_maps(self):
        self.fake.releases = [release_dict("rel_1")]
        self.env["livam.release"].action_sync()
        rel = self.env["livam.release"].search([("livam_id", "=", "rel_1")])
        self.assertEqual(rel.name, "beta 1.4.0")
        self.assertTrue(rel.enabled)

    def test_sync_saas_instances_maps_load(self):
        self.fake.saas_instances = [instance_dict("si_1")]
        self.env["livam.saas.instance"].action_sync()
        inst = self.env["livam.saas.instance"].search([("livam_id", "=", "si_1")])
        self.assertEqual(inst.active_tenant_count, 3)

    def test_sync_all_creates_every_model(self):
        self.fake.saas_instances = [instance_dict("si_1")]
        self.fake.licenses = [license_dict("lic_1")]
        self.fake.installations = [installation_item("inst_9", "lic_1")]
        self.fake.releases = [release_dict("rel_1")]
        self.env["livam.license"].action_sync_all()
        self.assertEqual(self.env["livam.license"].search_count([]), 1)
        self.assertEqual(self.env["livam.installation"].search_count([]), 1)
        self.assertEqual(self.env["livam.release"].search_count([]), 1)
        self.assertEqual(self.env["livam.saas.instance"].search_count([]), 1)

    # -- license write actions ---------------------------------------------

    def test_mark_paid(self):
        lic = self.env["livam.license"].create({"livam_id": "lic_1", "name": "hans"})
        self.fake.license_single = license_dict("lic_1", paymentStatus="paid")
        lic.action_mark_paid()
        self.assertIn(("POST", "/licenses/lic_1/mark-paid", None), self.fake.calls)

    def test_renew_uses_billing_cycle(self):
        lic = self.env["livam.license"].create(
            {"livam_id": "lic_1", "name": "hans", "billing_cycle": "yearly"}
        )
        self.fake.license_single = license_dict("lic_1")
        lic.action_renew()
        self.assertIn(
            ("POST", "/licenses/lic_1/renew", {"days": 365}), self.fake.calls
        )

    def test_suspend_and_activate(self):
        lic = self.env["livam.license"].create({"livam_id": "lic_1", "name": "hans"})
        self.fake.license_single = license_dict("lic_1", status="suspended")
        lic.action_suspend()
        self.fake.license_single = license_dict("lic_1", status="active")
        lic.action_activate()
        self.assertIn(("POST", "/licenses/lic_1/suspend", None), self.fake.calls)
        self.assertIn(("POST", "/licenses/lic_1/activate", None), self.fake.calls)

    def test_set_features(self):
        lic = self.env["livam.license"].create({"livam_id": "lic_1", "name": "hans"})
        self.fake.license_single = license_dict("lic_1")
        lic._set_features(["BILLING", "CMS"])
        self.assertIn(
            ("POST", "/licenses/lic_1/features", {"features": ["BILLING", "CMS"]}),
            self.fake.calls,
        )

    def test_move(self):
        inst = self.env["livam.saas.instance"].create(
            {"livam_id": "si_2", "ref": "inst_2", "name": "EU-Ost"}
        )
        lic = self.env["livam.license"].create({"livam_id": "lic_1", "name": "hans"})
        self.fake.license_single = license_dict("lic_1")
        lic._move(inst)
        self.assertIn(
            ("POST", "/licenses/lic_1/move", {"saasInstanceRef": "inst_2"}),
            self.fake.calls,
        )

    # -- wizards ------------------------------------------------------------

    def test_features_wizard_applies(self):
        lic = self.env["livam.license"].create({"livam_id": "lic_1", "name": "hans"})
        billing = self.env["livam.feature"].search([("key", "=", "BILLING")])
        cms = self.env["livam.feature"].search([("key", "=", "CMS")])
        self.fake.license_single = license_dict("lic_1")
        wizard = self.env["livam.license.features.wizard"].create(
            {
                "license_id": lic.id,
                "feature_ids": [(6, 0, (billing | cms).ids)],
            }
        )
        wizard.action_apply()
        self.assertIn(
            ("POST", "/licenses/lic_1/features", {"features": ["BILLING", "CMS"]}),
            self.fake.calls,
        )

    def test_move_wizard_applies(self):
        lic = self.env["livam.license"].create({"livam_id": "lic_1", "name": "hans"})
        inst = self.env["livam.saas.instance"].create(
            {"livam_id": "si_2", "ref": "inst_2", "name": "EU-Ost", "status": "active"}
        )
        self.fake.license_single = license_dict("lic_1")
        wizard = self.env["livam.move.license.wizard"].create(
            {"license_id": lic.id, "target_instance_id": inst.id}
        )
        wizard.action_move()
        self.assertIn(
            ("POST", "/licenses/lic_1/move", {"saasInstanceRef": "inst_2"}),
            self.fake.calls,
        )

    def test_saas_instance_wizard_registers(self):
        wizard = self.env["livam.saas.instance.wizard"].create(
            {
                "name": "EU-West",
                "ref": "eu-west-1",
                "base_url": "https://saas.example",
                "capacity": 10,
                "status": "active",
            }
        )
        wizard.action_register()
        self.assertIn(
            (
                "POST",
                "/saas-instances",
                {
                    "ref": "eu-west-1",
                    "displayName": "EU-West",
                    "baseUrl": "https://saas.example",
                    "capacity": 10,
                    "status": "active",
                },
            ),
            self.fake.calls,
        )

    # -- installation / release write actions -------------------------------

    def test_revoke_certificate(self):
        inst = self.env["livam.installation"].create(
            {"livam_id": "inst_9", "name": "uuid-1"}
        )
        self.fake.installation_single = installation_item("inst_9", None)
        inst.action_revoke_certificate()
        self.assertIn(
            ("POST", "/installations/inst_9/revoke-certificate", None),
            self.fake.calls,
        )

    def test_release_activate_and_deactivate(self):
        rel = self.env["livam.release"].create(
            {"livam_id": "rel_1", "name": "beta 1.4.0"}
        )
        rel.action_activate()
        rel.action_deactivate()
        self.assertIn(("POST", "/releases/rel_1/activate", None), self.fake.calls)
        self.assertIn(("POST", "/releases/rel_1/deactivate", None), self.fake.calls)

    def test_license_create_wizard(self):
        billing = self.env["livam.feature"].search([("key", "=", "BILLING")])
        wizard = self.env["livam.license.create.wizard"].create(
            {
                "license_type": "subscription",
                "max_instances": 1,
                "feature_ids": [(6, 0, billing.ids)],
                "auto_renew": False,
            }
        )
        wizard.action_create()
        self.assertIn(
            (
                "POST",
                "/licenses",
                {
                    "licenseType": "subscription",
                    "maxInstances": 1,
                    "features": ["BILLING"],
                    "autoRenew": False,
                },
            ),
            self.fake.calls,
        )



