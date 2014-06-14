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


class ProductTemplate(orm.Model):
    _inherit = "product.template"

    _columns = {
        'generate_main_display': fields.boolean('Generate Main Display'),
        'main_dim_id': fields.many2one(
            'attribute.attribute',
            string='Main Dimension',
            help=('This dimension will be used for generating '
                 'the product display')),
        'display_variant_ids': fields.one2many(
            'product.product',
            'product_tmpl_id',
            domain=[
                ('is_display', '=', True),
                '|',
                ('active', '=', True),
                ('active', '=', False),
                ], string='Display Variants'),
        'product_variant_ids': fields.one2many(
            'product.product',
            'product_tmpl_id',
            domain=[
                ('is_display', '=', False),
                '|',
                ('active', '=', True),
                ('active', '=', False),
                ], string='Product Variants'),
    }

    def _get_combinaison(self, cr, uid, product_temp, context=None):
        if context.get('product_display'):
            fields = [dim.name for dim in product_temp.dimension_ids]
            num_of_fields = len(fields)
            combinaisons = []
            if product_temp.main_dim_id:
                for value in product_temp.value_ids:
                    if value.dimension_id.id == product_temp.main_dim_id.id:
                        combinaisons.append(
                            [value.option_id.id] + [None]*(num_of_fields - 1)
                            )
            if product_temp.generate_main_display:
                combinaisons.append([None]*num_of_fields)
            return combinaisons
        return super(ProductTemplate, self)._get_combinaison(
            cr, uid, product_temp, context=context)

    def _prepare_variant_vals(self, cr, uid, product_temp, combinaison,
                              context=None):
        product_obj = self.pool['product.product']
        vals = super(ProductTemplate, self)._prepare_variant_vals(
            cr, uid, product_temp, combinaison, context=context)
        if context.get('product_display'):
            vals['is_display'] = True
            domain = [
                ['product_tmpl_id', '=', vals['product_tmpl_id']],
                ['is_display', '=', False],
            ]
            dimension = product_temp.main_dim_id
            if dimension and dimension.name in vals:
                domain.append([dimension.name, '=', vals[dimension.name]])
            product_ids = product_obj.search(cr, uid, domain, context=context)
            vals['display_for_product_ids'] = [(6, 0, product_ids)]
        return vals

    def _create_variant(self, cr, uid, product_temp, existing_product_ids,
                        context=None):
        created_product_ids = super(ProductTemplate, self)._create_variant(
            cr, uid, product_temp, existing_product_ids, context=context)
        if created_product_ids:
            self.pool['product.product'].update_existing_product_display(
                cr, uid, created_product_ids, context=context)

        ctx = context.copy()
        ctx['product_display'] = True
        created_product_display_ids = super(ProductTemplate, self).\
            _create_variant(cr, uid, product_temp, existing_product_ids,
                            context=ctx)
        return created_product_ids + created_product_display_ids


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def update_existing_product_display(self, cr, uid, ids, context=None):
        ids = self.search(cr, uid, [
            ['id', 'in', ids],
            ['is_display', '=', True]
            ], context=context)

        for product in self.browse(cr, uid, ids, context=context):
            domain = [
                ['product_tmpl_id', '=', product.product_tmpl_id.id],
                ['is_display', '=', False],
            ]
            dim = product.main_dim_id
            if dim and product[dim.name]:
                domain.append([dim.name, '=', product[dim.name].name])
            product_ids = self.search(cr, uid, domain, context=context)
            product.write({'display_for_product_ids': [(6, 0, product_ids)]})
        return True
