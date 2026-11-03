Requires :mod:`livam_connector` (configure LiVaM Base URL, Operator-Token and
Order-Webhook-Secret there) and the OCA ``contract`` module.

Set the following on a sale order (tab *LiVaM*) before confirmation:

* **Tenant-Wunschname** or **Eigene Domain** — exactly one of the two.
* **Abrechnungszyklus** — monthly or yearly.
* **Feature-Keys** — optional, comma-separated Lingavena feature keys.

A cron syncs paid invoices to LiVaM every hour.
