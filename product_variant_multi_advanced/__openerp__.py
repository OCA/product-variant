# -*- encoding: utf-8 -*-
##############################################################################
#
#    Model module for OpenERP
#    Copyright (C) 2010 Sébastien BEAU <sebastien.beau@akretion.comr>
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


{
    'name': 'Product Variant Multi Advanced',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module extend the capacity of product_variant_multi giving the posibility of building automatically the name, the description... of the product from the product template.
Due to some limit of the orm you will need to apply some patch on the server""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['product_variant_multi'],
    'init_xml': [],
    'update_xml': ['product.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

