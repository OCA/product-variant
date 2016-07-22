# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product supplier info per variant',
    'summary': 'Supplier info to product variant scope',
    'version': '8.0.1.0.0',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'category': 'Product Management',
    'depends': [
        'product',
    ],
    'data': [
        'views/product_template_view.xml',
    ],
    'installable': True,
    "post_init_hook": "duplicate_supplierinfo_per_variant",
}
