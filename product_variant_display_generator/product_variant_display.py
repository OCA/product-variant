# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP 
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   @author Chafique Delli <chafique.delli@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm

import logging
_logger = logging.getLogger(__name__)




class product_template(orm.Model):
    _inherit = "product.template"


    _columns = {
        'product_ids': fields.many2one('product.product', string='Products'),
        'is_displays': fields.boolean('Is Displays'),
    }

    _defaults = {
        'is_displays': False,
        'type': 'display',
    }

    def __init__(self, pool, cr):
        super(product_template, self).__init__(pool, cr)
        option = ('display', 'Product Display')
        type_selection = self._columns['type'].selection
        if option not in type_selection:
            type_selection.append(option)

