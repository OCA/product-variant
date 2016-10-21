# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba <alex.comba@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def _update_sale_delay(self, vals):
        values = {'sale_delay': vals['sale_delay']}
        self.product_variant_ids.write(values)

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'sale_delay' in vals:
            for product in self:
                product._update_sale_delay(vals)
        return res

    @api.model
    def create(self, vals):
        product_tmpl = super(ProductTemplate, self).create(vals)
        if 'sale_delay' in vals:
            for product in product_tmpl:
                product._update_sale_delay(vals)
        return product_tmpl
