# -*- coding: utf-8 -*-
# Copyright 2107 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    sale_delay = fields.Float(
        string='Customer Lead Time',
        help='The average delay in days between the confirmation of the '
             'customer order and the delivery of the finished products. '
             'It\'s the time you promise to your customers.')

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        template_vals = {}
        if 'sale_delay' not in vals:
            template_vals['sale_delay'] = product.product_tmpl_id.sale_delay
        if template_vals:
            product.write(template_vals)
        return product
