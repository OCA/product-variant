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


import logging
_logger = logging.getLogger(__name__)


class product_template(orm.Model):
    _inherit = "product.template"

    _columns = {
        'generate_main_display': fields.boolean('Generate Main Display'),
        'generate_display_from_dim_id': fields.many2one('product.variant.dimension',
                                                        string='Generate Display From Dimension'),
    }


    def _get_combinaison(self, cr, uid, product_temp, context=None):
        if context.get('product_display'):
            fields = [dimension.name for dimension in product_temp.dimension_ids]
            number_of_fields = len(fields)
            combinaisons = []
            if product_temp.generate_display_from_dim_id:
                for value in product_temp.value_ids:
                    if value.dimension_id.id == product_temp.generate_display_from_dim_id.id:
                        combinaisons.append([value.option_id.id] + [None]*(number_of_fields -1))
            if product_temp.generate_main_display:
                combinaisons.append([None]*number_of_fields)
            return combinaisons
        return super(product_template, self)._get_combinaison(cr, uid,
                                                              product_temp,
                                                              context=context)


    def _prepare_variant_vals(self, cr, uid, product_temp, combinaison, context=None):
        product_obj=self.pool['product.product']
        vals = super(product_template, self)._prepare_variant_vals(cr, uid,
            product_temp, combinaison, context=context)
        if context.get('product_display'):
            vals['is_display'] = True
            dimension_name = product_temp.generate_display_from_dim_id.name
            domain = [
                ['product_tmpl_id', '=', vals['product_tmpl_id']],
                ['is_display', '=', False],
            ]
            if dimension_name in vals:
                domain.append([dimension_name, '=', vals[dimension_name]])
            product_ids = product_obj.search(cr, uid, domain, context=context)
            vals['display_for_product_ids']=[(6, 0, product_ids)]
        return vals


    def _create_variant(self, cr, uid, product_temp, existing_product_ids, context=None):
        created_product_ids = super(product_template, self)._create_variant(cr, uid,
                                                             product_temp,
                                                             existing_product_ids,
                                                             context=context)
        ctx = context.copy()
        ctx['product_display'] = True
        created_product_display_ids = super(product_template, self)._create_variant(cr, uid,
                                                             product_temp,
                                                             existing_product_ids,
                                                             context=ctx)
        return created_product_ids + created_product_display_ids
