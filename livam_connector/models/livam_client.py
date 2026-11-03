"""LiVaM REST client, HMAC signing and error mapping.

This module is the transport foundation for every other ``livam_*`` addon. It
knows nothing about Odoo business models: it serialises JSON payloads into
signed HTTPS requests against the LiVaM API and returns decoded JSON.

Configuration is read from ``ir.config_parameter`` by :func:`get_livam_client`
so that credentials never live in code or logs.
"""

import hashlib
import hmac
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

_logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15


class LivamApiError(Exception):
    """Base class for every LiVaM API failure."""


class LivamConfigurationError(LivamApiError):
    """The client is not fully configured (fail closed)."""


class LivamAuthenticationError(LivamApiError):
    """Authentication/authorisation failed (HTTP 401/403) or a secret is missing."""


class LivamConnectionError(LivamApiError):
    """Transport-level failure (DNS, TLS, timeout, connection refused)."""


class LivamRequestError(LivamApiError):
    """LiVaM answered with a non-success, non-auth status (4xx/5xx)."""

    def __init__(self, status, message, url):
        super().__init__("[%s] %s (%s)" % (status, message, url))
        self.status = status
        self.url = url


def sign_webhook(secret, raw_body):
    """Return the ``sha256=<hex>`` HMAC-SHA256 value for ``raw_body``.

    ``raw_body`` must be the *raw* request body bytes — never a re-serialised
    dict — so that signing and LiVaM-side verification operate on identical
    bytes.
    """
    if not secret:
        raise LivamConfigurationError(
            "Order-Webhook-Secret ist nicht konfiguriert (fail closed)."
        )
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return "sha256=" + digest


class LivamClient:
    """Minimal JSON REST client for the LiVaM API."""

    def __init__(
        self,
        base_url,
        operator_token="",
        webhook_secret="",
        timeout=DEFAULT_TIMEOUT,
        urlopen=urlopen,
    ):
        self.base_url = (base_url or "").rstrip("/")
        self.operator_token = operator_token or ""
        self.webhook_secret = webhook_secret or ""
        self.timeout = timeout or DEFAULT_TIMEOUT
        self._urlopen = urlopen

    def _request(self, method, path, payload=None, auth="bearer"):
        if not self.base_url:
            raise LivamConfigurationError(
                "LiVaM Base URL ist nicht konfiguriert (fail closed)."
            )
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(
                payload, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            headers["Content-Type"] = "application/json"

        if auth == "bearer":
            if not self.operator_token:
                raise LivamConfigurationError(
                    "Operator-Token ist nicht konfiguriert (fail closed)."
                )
            headers["Authorization"] = "Bearer " + self.operator_token
        elif auth == "webhook":
            if data is None:
                raise LivamApiError(
                    "Webhook-Aufrufe benötigen einen Payload zum Signieren."
                )
            headers["X-Webhook-Signature"] = sign_webhook(
                self.webhook_secret, data
            )
        else:
            raise LivamApiError("Unbekannter Auth-Modus: %r" % auth)

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with self._urlopen(request, timeout=self.timeout) as response:
                return self._decode(response.read())
        except HTTPError as exc:
            self._raise_for_http(exc)
        except (URLError, OSError) as exc:
            raise LivamConnectionError(
                "LiVaM nicht erreichbar (%s): %s" % (url, exc)
            ) from exc

    @staticmethod
    def _decode(body):
        if not body:
            return None
        try:
            return json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return body.decode("utf-8", "replace")

    def _raise_for_http(self, exc):
        body = exc.read()
        detail = self._decode(body)
        if isinstance(detail, dict):
            message = detail.get("error") or detail.get("message") or ""
        elif isinstance(detail, str):
            message = detail
        else:
            message = ""
        if exc.code in (401, 403):
            raise LivamAuthenticationError(
                "LiVaM-Authentifizierung fehlgeschlagen (HTTP %s)." % exc.code
            )
        raise LivamRequestError(exc.code, message or exc.reason, exc.url)

    # -- order webhook (HMAC) ----------------------------------------------

    def create_order(self, payload):
        """``POST /webhooks/orders``, HMAC-signed."""
        return self._request("POST", "/webhooks/orders", payload, auth="webhook")

    def check_tenant_availability(self, tenant_slug=None, domain=None):
        """``POST /tenants/check-availability``, HMAC-signed."""
        payload = {}
        if tenant_slug:
            payload["tenantSlug"] = tenant_slug
        if domain:
            payload["domain"] = domain
        if not payload:
            raise LivamApiError("tenant_slug oder domain muss gesetzt sein.")
        return self._request(
            "POST", "/tenants/check-availability", payload, auth="webhook"
        )

    # -- operator API (Bearer) ---------------------------------------------

    def operator_request(self, method, path, payload=None):
        """Generic operator-API call, Bearer-authenticated."""
        return self._request(method, path, payload, auth="bearer")


def get_livam_client(env):
    """Build a :class:`LivamClient` from ``ir.config_parameter`` values."""
    params = env["ir.config_parameter"].sudo()

    def get_param(key, default=""):
        return params.get_param(key, default) or default

    raw_timeout = get_param("livam.timeout", str(DEFAULT_TIMEOUT))
    try:
        timeout = int(raw_timeout)
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT
    return LivamClient(
        base_url=get_param("livam.base_url"),
        operator_token=get_param("livam.operator_token"),
        webhook_secret=get_param("livam.webhook_secret"),
        timeout=timeout,
    )

