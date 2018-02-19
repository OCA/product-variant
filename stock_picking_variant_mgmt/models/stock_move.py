# -*- coding: utf-8 -*-
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        related="product_id.attribute_value_ids",
        readonly=True,
    )
