# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product variant template reassign",
    "summary": "Reassign variants to templates",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Product",
    "website": "https://github.com/OCA/product-variant",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu"],
    "license": "AGPL-3",
    "depends": ["product", "sale_stock"],
    "external_dependencies": {"python": ["openupgradelib"]},
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "wizards/reassign_variant_views.xml",
    ],
}
