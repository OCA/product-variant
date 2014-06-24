# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Product Variant Generator Price",
    "version": "1.0",
    "author": "OpenERP SA, Akretion",
    "category": "Sales Management",
    "license": "AGPL-3",
    "summary": "Product Prices with multi-dimension variants",
    "description": """

    """,
    "depends" : [
                "product_variant_generator",
                ],
    "data" : [
        "product_view.xml",
    ],
    "application": True,
    "active": False,
    "installable": True,
}
