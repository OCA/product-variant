# Copyright 2020 Studio73 - Miguel Gandia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Product Matrix Sticky Table Header",
    "summary": """
       Technical module: Add sticky header for Matrix Product
    """,
    "category": "Sales/Sales",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "author": "Studio73," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "depends": ["product_matrix"],
    "qweb": [
        "static/src/xml/product_matrix.xml",
    ],
    "data": ["views/assets.xml"],
    "installable": True,
}
