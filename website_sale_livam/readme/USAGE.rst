In the website checkout the customer chooses:

* a **tenant name** (subdomain) or an **own domain** — exactly one,
* the **billing cycle** (monthly/yearly).

The availability of the name/domain is checked live against LiVaM and again on
form submission. The values are stored on the sale order and trigger the
LiVaM provisioning on order confirmation (see :mod:`livam_sale`).
