Build a client from the configured parameters::

    from odoo.addons.livam_connector.models.livam_client import get_livam_client

    client = get_livam_client(env)
    client.create_order({...})                    # signed order webhook
    client.check_tenant_availability(tenant_slug="hans")
    client.operator_request("GET", "/licenses")   # bearer-authenticated
