# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Product Discogs Configurator",
    "summary": "Create products and variants from discogs",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/product-variant",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product_disc",
        "product_variant_configurator",
    ],
    "data": [
        "views/product_template.xml",
        "views/res_partner.xml",
    ],
}
