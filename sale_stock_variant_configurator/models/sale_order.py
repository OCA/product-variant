# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Redefine again the product template field as a regular one
    product_tmpl_id = fields.Many2one(
        string='Product Template',
        comodel_name='product.template',
        store=True,
        related=False,
        auto_join=True,
    )
