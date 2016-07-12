# -*- coding: utf-8 -*-
# © 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Variant Sale Price",
    "summary": "Sale price by variant",
    "version": "8.0.1.0.0",
    "category": "Product Management",
    "license": "AGPL-3",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    'website': "http://www.agilebg.com",
    "depends": [
        "sale",
    ],
    "data": [
        "data/product_product_data.xml",
        "views/product_view.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
