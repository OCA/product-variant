# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # This field is for avoiding conflicts with other modules adding the same
    # field. This field name for sure won't conflict
    product_tmpl_id_purchase_order_variant_mgmt = fields.Many2one(
        comodel_name="product.template", related="product_id.product_tmpl_id",
        readonly=True
    )
    state_purchase_order_variant_mgmt = fields.Selection(
        related="order_id.state",
        readonly=True,
        string="Order status"
    )
    product_attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        related="product_id.attribute_value_ids",
        readonly=True
    )
