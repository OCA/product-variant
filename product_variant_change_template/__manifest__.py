# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Variant Change Template",
    "summary": "Move existing variants to another template keeping their identity",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Product",
    "website": "https://github.com/OCA/product-variant",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["carlosdauden"],
    "license": "AGPL-3",
    "depends": ["product"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/product_variant_change_template_views.xml",
    ],
}
