# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Handle easily multiple variants on Sales Orders',
    'summary': 'Handle the addition/removal of multiple variants from '
               'product template into the sales order',
    'version': '11.0.2.0.0',
    'author': 'Tecnativa,'
              'Odoo Community Association (OCA)',
    'category': 'Sale',
    'license': 'AGPL-3',
    'website': 'https://www.tecnativa.com',
    'depends': [
        'sale',
        'onchange_helper',
        'web_widget_x2many_2d_matrix',
    ],
    'demo': [],
    'data': [
        'wizard/sale_manage_variant_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
