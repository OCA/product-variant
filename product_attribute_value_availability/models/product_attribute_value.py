# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    is_available = fields.Boolean(
        string="Available",
        default=True,
        help="Uncheck to prevent selling this value on every product.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "is_available" in vals:
            # product.template._get_first_possible_variant_id is ormcached
            # and depends on the possible combinations.
            self.env.registry.clear_cache()
        return res
