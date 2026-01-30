# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    def write(self, vals):
        res = super().write(vals)
        if "name" in vals:
            ptavs = self.env["product.template.attribute.value"].search(
                [("product_attribute_value_id", "in", self.ids)]
            )
            ptavs.ptav_product_variant_ids.assign_search_name_all_langs()
        return res
