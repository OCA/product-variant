# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        vals_to_update = {}
        if 'sale_delay' in vals:
            vals_to_update['sale_delay'] = vals['sale_delay']
        self.mapped('product_variant_ids').write(vals_to_update)
        return res

    @api.model
    def create(self, vals):
        product_tmpl = super(ProductTemplate, self).create(vals)
        vals_to_update = {}
        if 'sale_delay' in vals:
            vals_to_update['sale_delay'] = vals['sale_delay']
            product_tmpl.product_variant_ids.write(vals_to_update)
        return product_tmpl
