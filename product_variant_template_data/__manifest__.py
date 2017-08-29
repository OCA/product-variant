# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Variant Template Data',
    'summary': 'Data template in product level',
    'version': '10.0.1.0.0',
    'category': 'Product Management',
    'license': 'AGPL-3',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'https://www.agilebg.com/',
    'depends': [
        'stock',
    ],
    'data': [
        'views/product_product_view.xml'
    ],
    'installable': True,
}
