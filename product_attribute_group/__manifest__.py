# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Product Attribute Group",
    "summary": "Add group on product attribute value",
    "version": "12.0.1.0.0",
    "category": "Product Management",
    "website": "https://github.com/OCA/product-variant",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["product"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_attribute_group_view.xml",
        "views/product_attribute_value.xml",
    ],
    "demo": [],
    "qweb": [],
}
