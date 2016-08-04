# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# © 2016 Raphaël REVERDY @ Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product Variant Search by Attributes',
    'summary': """Allows to search product variants matching several keywords
                  in their attribute values.""",
    'version': '8.0.0.0.1',
    'category': 'Product',
    'author': 'Akretion',
    'depends': [
        'product',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
