# Copyright 2020 Studio73 - Miguel Gandia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Product Matrix Show Color",
    "summary": """
       Technical module: Show attribute color in product matrix table
    """,
    "category": "Sales/Sales",
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    "author": "Studio73," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "depends": ["product_matrix"],
    "assets": {
        "web.assets_backend": [
            "product_matrix_show_color/static/src/scss/product_matrix.scss",
        ],
        "web.assets_qweb": [
            "product_matrix_show_color/static/src/xml/product_matrix.xml",
        ],
    },
    "installable": True,
}
