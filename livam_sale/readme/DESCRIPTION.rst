Provision a LiVaM license from a confirmed sale order.

On order confirmation the module calls the signed LiVaM order webhook, stores
the returned license id, creates a recurring OCA ``contract`` and later syncs
paid invoices back to LiVaM (``mark-paid`` / ``renew``).
