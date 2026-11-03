After installation open *Settings → LiVaM* and set:

* **LiVaM Base URL** — base URL of the LiVaM instance (e.g.
  ``https://lus.lingavena.de``).
* **Operator-Token** — the ``LIVAM_OPERATOR_TOKEN`` used for the operator API.
* **Order-Webhook-Secret** — the ``LIVAM_ORDER_WEBHOOK_SECRET`` used to sign
  shop webhooks.

All values are stored in ``ir.config_parameter`` and never logged.
