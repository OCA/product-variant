# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba <alex.comba@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Variant Sale Delay',
    'summary': 'Customer Lead Time in product level',
    'version': '8.0.1.0.0',
    'category': 'Product Management',
    'license': 'AGPL-3',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'https://www.agilebg.com',
    'depends': [
        'stock'
    ],
    'post_init_hook': 'post_init_hook',
}
