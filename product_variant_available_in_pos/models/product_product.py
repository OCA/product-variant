# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    available_in_pos = fields.Boolean(
        string='Available in the Point of Sale',
        help='Check if you want this product to appear in the Point of Sale')

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        template_vals = {}
        if 'available_in_pos' not in vals:
            template_vals[
                'available_in_pos'] = product.product_tmpl_id.available_in_pos
        if template_vals:
            product.write(template_vals)
        return product
