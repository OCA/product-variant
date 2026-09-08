# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Variant Name",
    "version": "19.0.1.0.0",
    "category": "Product",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "license": "AGPL-3",
    "depends": [
        "product",
    ],
    "data": ["views/product_view.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
