{
    "name": "LiVaM Sale",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "license": "AGPL-3",
    "summary": "Provision a LiVaM license from a confirmed sale order",
    "author": "LiVaM",
    "website": "https://github.com/MBadberg/livam-odoo",
    "depends": ["sale", "contract", "livam_connector"],
    "data": [
        "data/ir_cron.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
