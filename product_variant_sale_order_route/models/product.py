# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.product'

    sale_order_line_route_id = fields.Many2one(
        comodel_name='stock.location.route',
        string="Route for Sale Order",
        domain=[('sale_selectable', '=', True)],
    )
