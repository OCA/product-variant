# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product supplier info per variant',
    'summary': 'Supplier info to product variant scope',
    'version': '8.0.1.0.0',
    'author': 'Tecnativa, Akretion,'
              'Odoo Community Association (OCA)',
    'category': 'Product Management',
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
    'installable': True,
}
