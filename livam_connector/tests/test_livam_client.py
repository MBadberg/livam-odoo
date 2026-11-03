import io
import json
from urllib.error import HTTPError, URLError

from odoo.tests.common import TransactionCase

from odoo.addons.livam_connector.models.livam_client import (
    LivamAuthenticationError,
    LivamApiError,
    LivamConfigurationError,
    LivamConnectionError,
    LivamRequestError,
    LivamClient,
    sign_webhook,
)


class _FakeResponse:
    def __init__(self, body=b"", status=200):
        self._body = body
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class _RecordingUrlopen:
    """Records every call and returns the next queued response/exception."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, request, timeout=None):
        self.calls.append((request, timeout))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class TestSignWebhook(TransactionCase):
    def test_signature_is_prefixed_and_stable(self):
        secret = "topsecret"
        body = b'{"orderId":"SO1"}'
        signature = sign_webhook(secret, body)
        self.assertTrue(signature.startswith("sha256="))
        self.assertEqual(signature, sign_webhook(secret, body))

    def test_missing_secret_fails_closed(self):
        with self.assertRaises(LivamConfigurationError):
            sign_webhook("", b"{}")


class TestLivamClient(TransactionCase):
    def make_client(self, responses, **kwargs):
        opener = _RecordingUrlopen(responses)
        client = LivamClient(
            base_url="https://lus.example/",
            operator_token="op-token",
            webhook_secret="ws-secret",
            urlopen=opener,
            **kwargs,
        )
        return client, opener

    def test_bearer_get(self):
        client, opener = self.make_client([_FakeResponse(b'{"ok":true}')])
        result = client.operator_request("GET", "/licenses")
        self.assertEqual(result, {"ok": True})
        request = opener.calls[0][0]
        self.assertEqual(request.full_url, "https://lus.example/licenses")
        self.assertEqual(request.get_header("Authorization"), "Bearer op-token")

    def test_webhook_request_is_signed_with_raw_body(self):
        client, opener = self.make_client([_FakeResponse(b'{"available":true}')])
        result = client.check_tenant_availability(tenant_slug="hans")
        self.assertEqual(result, {"available": True})
        request = opener.calls[0][0]
        self.assertEqual(
            request.get_header("X-webhook-signature"),
            sign_webhook("ws-secret", request.data),
        )
        self.assertEqual(json.loads(request.data), {"tenantSlug": "hans"})

    def test_create_order_posts_to_webhook(self):
        client, opener = self.make_client(
            [_FakeResponse(b'{"license":{"id":"lic_1"}}')]
        )
        result = client.create_order(
            {"orderId": "SO1", "tenantSlug": "hans"}
        )
        self.assertEqual(result["license"]["id"], "lic_1")
        request = opener.calls[0][0]
        self.assertEqual(request.full_url, "https://lus.example/webhooks/orders")

    def test_availability_requires_identifier(self):
        client, _opener = self.make_client([])
        with self.assertRaises(LivamApiError):
            client.check_tenant_availability()

    def test_missing_base_url_fails_closed(self):
        client = LivamClient("", operator_token="op-token")
        with self.assertRaises(LivamConfigurationError):
            client.operator_request("GET", "/licenses")

    def test_missing_operator_token_fails_closed(self):
        client = LivamClient("https://lus.example", operator_token="")
        with self.assertRaises(LivamConfigurationError):
            client.operator_request("GET", "/licenses")

    def test_connection_error_is_mapped(self):
        client, _opener = self.make_client([URLError("boom")])
        with self.assertRaises(LivamConnectionError):
            client.operator_request("GET", "/licenses")

    def test_http_error_maps_status_and_body(self):
        client = LivamClient("https://lus.example")
        exc = HTTPError(
            "https://lus.example/x",
            400,
            "Bad Request",
            {},
            io.BytesIO(b'{"error":"bad"}'),
        )
        with self.assertRaises(LivamRequestError) as caught:
            client._raise_for_http(exc)
        self.assertEqual(caught.exception.status, 400)

    def test_auth_error_maps_401(self):
        client = LivamClient("https://lus.example")
        exc = HTTPError(
            "https://lus.example/x",
            401,
            "Unauthorized",
            {},
            io.BytesIO(b""),
        )
        with self.assertRaises(LivamAuthenticationError):
            client._raise_for_http(exc)
