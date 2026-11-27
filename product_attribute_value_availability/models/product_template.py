# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _is_combination_possible(
        self, combination, parent_combination=None, ignore_no_variant=False
    ):
        unavailable = combination._filter_unavailable()
        if ignore_no_variant:
            unavailable = unavailable._without_no_variant_attributes()
        if unavailable:
            return False
        return super()._is_combination_possible(
            combination,
            parent_combination=parent_combination,
            ignore_no_variant=ignore_no_variant,
        )

    def _get_attribute_exclusions(
        self, parent_combination=None, parent_name=None, combination_ids=None
    ):
        res = super()._get_attribute_exclusions(
            parent_combination=parent_combination,
            parent_name=parent_name,
            combination_ids=combination_ids,
        )
        lines = self.valid_product_template_attribute_line_ids
        unavailable = lines.product_template_value_ids._filter_unavailable()
        res["unavailable_ptav_ids"] = unavailable.ids
        return res
