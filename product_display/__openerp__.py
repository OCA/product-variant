# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Chafique Delli
#    Copyright 2013 Akretion
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{'name' : 'Product Display',
 'version' : '1.0',
 "author": "Akretion",
 'category': 'Sales Management',
 'description': """
Product Display
================

A simple module for handling the product display.
It provides view for product display,
so they can be created manually. It doesn't provide
all the bells and whistles of the product_variant_display
module (creator wizards, ...).

""",
 'author' : 'Akretion',
 'maintainer': 'Akretion',
 'website': 'http://www.akretion.com/',
 'depends' : [
    'product',
    ],
 'data': [
    'product_view.xml',
    ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 }
