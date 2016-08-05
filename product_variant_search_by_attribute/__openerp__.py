# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# © 2016 Raphaël REVERDY @ Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product Variant Search by Attributes',
    'summary': """Allows searching inside the product variant attributes
                  all attributes at once with multiple keywords""",
    'version': '8.0.1.0.0',
    'category': 'Product',
    'author': ['Akretion', 'Odoo Community Association (OCA)'],
    'depends': [
        'product',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'data/config_data.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
