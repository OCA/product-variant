# -*- coding: utf-8 -*-
# Copyright 2014 AvancOSC - Alfredo de la Fuente
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2014 Shine IT - Tony Gu
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Product Variant Default Code',
    'version': '10.0.1.0.0',
    'author': 'AvancOSC,'
              'Shine IT,'
              'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'category': 'Product',
    'depends': [
        'product',
    ],
    'data': [
        'views/product_attribute_value_view.xml',
        'views/product_view.xml',
    ],
    'installable': True
}
