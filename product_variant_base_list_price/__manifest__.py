# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Variant Base List Price",
    "summary": """This module allows to define a base pricelist on which base
    the displayed sale price on variants""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "depends": ["sale", "base_partition"],
    "data": ["views/product_product.xml", "views/res_config_settings.xml"],
}
