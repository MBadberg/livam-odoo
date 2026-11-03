{
    "name": "LiVaM Website Sale",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "license": "AGPL-3",
    "summary": "Tenant name/domain and billing cycle selection in the LiVaM shop checkout",
    "author": "LiVaM",
    "website": "https://github.com/MBadberg/livam-odoo",
    "depends": ["website_sale", "livam_sale"],
    "data": [
        "data/checkout_step.xml",
        "views/checkout_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_livam/static/src/js/livam_checkout.js",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
