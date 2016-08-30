# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def _update_available_in_pos(self, vals):
        values = {'available_in_pos': vals['available_in_pos']}
        self.product_variant_ids.write(values)

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'available_in_pos' in vals:
            for product in self:
                product._update_available_in_pos(vals)
        return res

    @api.model
    def create(self, vals):
        product_tmpl = super(ProductTemplate, self).create(vals)
        if 'available_in_pos' in vals:
            for product in product_tmpl:
                product._update_available_in_pos(vals)
        return product_tmpl
