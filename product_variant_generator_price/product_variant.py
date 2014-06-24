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

from openerp.osv import fields, orm


class ProductTemplate(orm.Model):
    _inherit = "product.template"

    _columns = {
        'automatic_price_extra': fields.boolean("Automatic Price Extra"),
    }


class ProductProduct(orm.Model):
    _inherit = "product.product"

    def _get_price_extra(self, cr, uid, ids, field_names=None, arg=False,
                         context=None):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            price_extra = 0.00
            if product.automatic_price_extra:
                for dimension in product.dimension_ids:
                    option = product[dimension.name]
                    if option:
                        for dimension_value in product.value_ids:
                            if dimension_value.option_id.id == option.id:
                                price_extra += dimension_value.price_extra
                                break
            else:
                price_extra = product.manual_price_extra
            res[product.id] = price_extra
        return res

    def _set_extra_price(self, cr, uid, ids, field_names=None, value=None,
                         arg=False, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for product in self.browse(cr, uid, ids, context=context):
            if not product.automatic_price_extra:
                self.write(
                    cr, uid, product.id, {'manual_price_extra': value},
                    context=context)
            else:
                price = self._get_price_extra(
                    cr, uid, [product.id], field_names=field_names, arg=arg,
                         context=context)[product.id]
                cr.execute("""update product_product set
                    price_extra=%s where id=%s""", (price, product.id))
        return True

    def _get_products_from_product_template(self, cr, uid, ids, context=None):
        return self.get_products_from_product_template(
            cr, uid, ids, context=context)

    def _get_products_from_dimension_value(self, cr, uid, ids, context=None):
        res = []
        for value in self.browse(cr, uid, ids, context=context):
            res += self.pool['product.product'].search(cr, uid,
                [('product_tmpl_id', '=', value.product_tmpl_id.id),
                 (value.dimension_id.name, '=', value.option_id.id)],
                context=context)
        return res

    _columns = {
        'price_extra': fields.function(
            _get_price_extra,
            type='float',
            fnct_inv=_set_extra_price,
            string='Price Extra',
            store ={
                'product.product': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['product_tmpl_id', 'manual_price_extra'],
                    10),
                'product.template': (
                    _get_products_from_product_template,
                    ['automatic_price_extra'],
                    10),
                'dimension.value': (
                    _get_products_from_dimension_value,
                    ['price_extra'],
                    10)
                },
            ),
        'manual_price_extra': fields.float('Manual Price Extra'),
    }


class DimensionValue(orm.Model):
    _inherit = "dimension.value"

    _columns = {
        'price_extra': fields.float('Price Extra'),
    }

    _defaults = {
        'price_extra': 0,
    }
