Confirm a sale order with a tenant identifier set. The module then:

1. calls ``POST /webhooks/orders`` (HMAC-signed) and stores the license id,
2. creates a recurring ``contract.contract`` (monthly or yearly),
3. on the first paid invoice calls ``POST /licenses/:id/mark-paid`` and on each
   later paid invoice ``POST /licenses/:id/renew`` (via the hourly cron).

The flow is fail-closed: a failed provisioning call rolls back the order
confirmation.
