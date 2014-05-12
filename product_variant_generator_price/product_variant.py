# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Akretion (www.akretion.com). All Rights Reserved
#    @author Chafique Delli <chafique.delli@akretion.com>
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

from openerp.osv import fields,orm


class product_product(orm.Model):
    _inherit = "product.product"

    def _get_price_extra(self, cr, uid, ids, field_names=None, arg=False, context=None):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            automatic = False
            if field_names=='price_extra':
                automatic = self.pool.get('product.template').read(
                    cr, uid,
                    product.product_tmpl_id.id, ['generate_price_extra'],
                    context=context)['generate_price_extra']
                price_extra = 0.00
                if automatic:
                    for dimension in product.product_tmpl_id.dimension_ids:
                        option = self.read(
                            cr, uid,
                            product.id, [dimension.name],
                            context=context)[dimension.name]
                        if option:
                            price = self.pool.get('attribute.option').read(
                                cr, uid, option[0], ['price'], context=context)
                            price_extra += price['price']
                else:
                    price_extra = self.read(
                        cr, uid,
                        product.id, ['manual_price_extra'],
                        context=context)['manual_price_extra']
                res[product.id] = price_extra
        return res

    def _set_extra_price(self, cr, uid, id, field_names=None, value=None, arg=False, context=None):
        self.write(cr, uid, id, {'manual_price_extra': value}, context=context)


    _columns = {
        'price_extra': fields.function(_get_price_extra, type='float',
                                       fnct_inv=_set_extra_price,
                                       string='Price Extra'),
        'manual_price_extra': fields.float('Manual Price Extra'),
    }



class product_variant_dimension_value(orm.Model):
    _inherit = "product.variant.dimension.value"

    _columns = {
        'price_option': fields.related('option_id', 'price', type='float',
                               relation='product.variant.dimension.option',
                               string="Price", readonly=True),
    }

    _defaults = {
        'price_option': 0,
    }


class product_template(orm.Model):
    _inherit = "product.template"

    _columns = {
        'generate_price_extra': fields.boolean("Generate Price Extra"),
    }
