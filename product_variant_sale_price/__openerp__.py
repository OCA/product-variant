# -*- coding: utf-8 -*-
# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Product Variant Sale Price',
    'summary': 'Allows to write fixed prices in product variants',
    'version': '8.0.1.0.0',
    'category': 'Product Management',
    'website': 'https://odoo-community.org/',
    'author': 'Tecnativa S.L., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'account',
        'product',
    ],
    'data': [
        'views/product_view.xml',
    ],
    'post_init_hook': 'set_sale_price_on_variant',
}
