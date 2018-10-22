# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Product supplier info per variant',
    'summary': 'Supplier info to product variant scope',
    'version': '11.0.1.0.0',
    'author': 'Tecnativa, '
              'Akretion, '
              'Odoo Community Association (OCA)',
    'category': 'Product Management',
    'website': 'https://github.com/OCA/product-variant'
    'depends': [
        'purchase',
    ],
    'data': [
        'views/product_product_view.xml',
        'views/product_supplierinfo_view.xml',
    ],
    'demo': [
        'demo/product_demo.xml',
        'demo/procurement_demo.xml',
    ],
}
