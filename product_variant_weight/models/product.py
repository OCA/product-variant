# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _prepare_weight_values(self, vals):
        values = {}
        if 'weight' in vals:
            values['weight'] = vals['weight']
        if 'weight_net' in vals:
            values['weight_net'] = vals['weight_net']
        return values

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for product in self:
            values = self._prepare_weight_values(vals)
            if values:
                product.product_variant_ids.write(values)
        return res

    @api.model
    def create(self, vals):
        product_tmpl = super(ProductTemplate, self).create(vals)
        for product in product_tmpl:
            values = self._prepare_weight_values(vals)
            if values:
                product.product_variant_ids.write(values)
        return product_tmpl


class ProductProduct(models.Model):
    _inherit = 'product.product'

    weight = fields.Float(
        string='Gross Weight', digits=dp.get_precision('Stock Weight'),
        help='The gross weight in Kg.')
    weight_net = fields.Float(
        string='Weight Net', digits=dp.get_precision('Stock Weight'),
        help='The net weight in Kg.')
