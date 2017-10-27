# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Handle easily multiple variants on Stock Pickings',
    'summary': 'Handle the addition/removal of multiple variants and the '
               'quantities transferred in the Pickings.',
    'version': '10.0.1.0.0',
    'author': 'Tecnativa,'
              'Odoo Community Association (OCA)',
    'category': 'Inventory, Logistics, Warehousing',
    'license': 'AGPL-3',
    'website': 'https://www.tecnativa.com',
    'depends': [
        'stock',
        'web_widget_x2many_2d_matrix',
    ],
    'data': [
        'wizard/stock_manage_variant_view.xml',
        'wizard/stock_transfer_manage_variant_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
}
