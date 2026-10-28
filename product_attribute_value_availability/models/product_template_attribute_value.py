# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    is_available = fields.Boolean(related="product_attribute_value_id.is_available")

    def _filter_unavailable(self):
        return self.filtered(lambda ptav: not ptav.is_available)
