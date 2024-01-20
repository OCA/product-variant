# Copyright 2023 Rosen Vladimirov, BioPrint Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Variant Create",
    "summary": """
        Wizard for create variant""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Rosen Vladimirov, BioPrint Ltd.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "depends": [
        "product",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/product_variant_create.py.xml",
    ],
    "demo": [],
}
