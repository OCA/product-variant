# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Product Variant Compare Price",
    "summary": "Allows to display discounts on the website at variant level",
    "version": "16.0.1.0.0",
    "category": "Product Management",
    "website": "https://github.com/OCA/product-variant",
    "author": "Odoo Community Association (OCA)",
    "maintainers": ["ecino"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["website_sale"],
    "data": [
        "views/product_views.xml",
    ],
}
