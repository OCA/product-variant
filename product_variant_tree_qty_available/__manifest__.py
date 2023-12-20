# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Variant Tree View Qty Available",
    "summary": "Adds the 'QTY' button to product variant tree view",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/product-variant",
    "author": "Ooops, Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "maintainers": ["dessanhemrayev", "CetmixGitDrone"],
    "installable": True,
    "depends": ["stock"],
    "data": [
        "views/product_views.xml",
    ],
}
