# Copyright 2022 ForgeFlow S.L. <https://forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Variant Configurator Manual Creation",
    "summary": "Provides a wizards to make variants on demand",
    "version": "15.0.1.0.0",
    "category": "Product Variant",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "depends": ["product", "product_variant_configurator"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/wizard_product_variant_configurator_manual_creation_view.xml",
        "views/product_template_view.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["ChrisOForgeFlow"],
}
