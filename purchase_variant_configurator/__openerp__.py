# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Purchase - Product variants",
    "summary": "Product variants in purchase management",
    'version': '9.0.1.0.0',
    "license": "AGPL-3",
    "depends": [
        "product",
        "purchase",
        "product_variant_configurator",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "website": "http://www.odoomrp.com",
    "data": [
        "views/inherited_purchase_order_views.xml",
        "views/inherited_product_product_views.xml"
    ],
    "installable": True,
    "post_init_hook": "assign_product_template",
}
