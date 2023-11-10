# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Variant Inactive",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "license": "AGPL-3",
    "category": "Product",
    "version": "14.0.2.0.2",
    "depends": ["product"],
    "data": [
        "views/product_template_view.xml",
        "views/product_variant_view.xml",
    ],
    "demo": ["data/product.product.csv"],
    "uninstall_hook": "uninstall_hook",
}
