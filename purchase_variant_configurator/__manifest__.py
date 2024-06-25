# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase - Product variants",
    "summary": "Product variants in purchase management",
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "depends": ["purchase", "product_variant_configurator"],
    "author": "AvanzOSC, "
    "Tecnativa, "
    "ACSONE SA/NV, "
    "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/product-variant",
    "data": [
        "views/inherited_purchase_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "post_init_hook": "assign_product_template",
}
