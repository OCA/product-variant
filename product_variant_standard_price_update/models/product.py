# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _compute_same_cost_variants(self):
        for template in self:
            cost = template.mapped('product_variant_ids.standard_price')
            if cost and cost.count(cost[0]) == len(cost):
                template.same_cost_variants = True

    @api.multi
    def _compute_product_template_field(self):
        for template in self:
            if len(template.product_variant_ids) > 1:
                variant_prices = template.mapped(
                    'product_variant_ids.standard_price')
                template.standard_price = min(variant_prices)
            else:
                template.standard_price = \
                    template.product_variant_ids.standard_price

    same_cost_variants = fields.Boolean(
        compute=_compute_same_cost_variants,
        string='All variants have the same cost',
    )
    standard_price = fields.Float(compute=_compute_product_template_field)

    @api.multi
    def write(self, vals):
        if 'standard_price' in vals:
            variants = self.mapped('product_variant_ids')
            variants.write({
                'standard_price': vals['standard_price'],
            })
        return super(ProductTemplate, self).write(vals)
