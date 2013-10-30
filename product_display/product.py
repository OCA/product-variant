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

from openerp.osv import orm, fields


class product_display(orm.Model):
    _name = 'product.display'
    _inherits = {'product.product': 'product_ids'}


    def _type_selection(self, cr, uid, context=None):
        selection=[]
        template_obj= self.pool.get('product.template')
        selection = template_obj._columns['type'].selection
        if ('display', 'Display Product') not in selection:
            selection += [('display', 'Display Product')]
        return selection

    _columns = {
        'product_ids': fields.many2one('product.product', string='Products',
                                       required=True, ondelete='cascade'),
        'type': fields.selection(_type_selection, string='Product Type'),
        'attribute_ids': fields.many2one('attribute.attribute',
                                         string='Attribute',
                                         required=True),
        'attribute_options': fields.many2one('attribute.option',
                                             string='Attribute Option',
                                             required=True),
    }

    _defaults = {
        'type': 'display',
    }

    _sql_constraints = [('product_display_unique','unique(product_ids, attribute_ids, attribute_options)',
                         'Product Display must be unique!')]
