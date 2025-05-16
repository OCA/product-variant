# Copyright 2022 ForgeFlow S.L. <https://forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_pending_variants = fields.Boolean(
        string="Has pending variants?",
        compute="_compute_pending_variants",
    )

    def _get_all_variant_combinations(self):
        lines_without_no_variants = (
            self.valid_product_template_attribute_line_ids._without_no_variant_attributes()
        )
        return itertools.product(
            *[
                ptal.product_template_value_ids._only_active()
                for ptal in lines_without_no_variants
            ]
        )

    def _get_existing_variants(self):
        all_variants = self.product_variant_ids.sorted(
            lambda p: (p.active, p.id and -p.id or False)
        )
        return {
            variant.product_template_attribute_value_ids: variant
            for variant in all_variants
        }

    @api.model
    def _get_variant_combination(self, combination_tuple):
        combination = self.env["product.template.attribute.value"].concat(
            *combination_tuple
        )
        if not self._is_combination_possible_by_config(
            combination, ignore_no_variant=True
        ):
            combination = False
        return combination

    @api.model
    def _can_add_variant(self, value):
        return not (
            isinstance(value.attribute_id.id, models.NewId)
            or isinstance(value.product_attribute_value_id.id, models.NewId)
        )

    @api.depends(
        "product_variant_ids",
        "attribute_line_ids",
        "attribute_line_ids.attribute_id",
        "attribute_line_ids.value_ids",
    )
    def _compute_pending_variants(self):
        for rec in self:
            has_pending_variants = False
            all_combinations = self._get_all_variant_combinations()
            existing_variants = self._get_existing_variants()
            for combination_tuple in all_combinations:
                combination = self._get_variant_combination(combination_tuple)
                if combination and combination not in existing_variants:
                    for value in combination:
                        if self._can_add_variant(value):
                            has_pending_variants = True
                            break
                if has_pending_variants:
                    break
            rec.has_pending_variants = has_pending_variants

    def _get_values_without_variant(self):
        all_combinations = self._get_all_variant_combinations()
        existing_variants = self._get_existing_variants()
        values_without_variant = {}
        for combination_tuple in all_combinations:
            combination = self._get_variant_combination(combination_tuple)
            if combination and combination not in existing_variants:
                for value in combination:
                    if self._can_add_variant(value):
                        values_without_variant.setdefault(
                            value.attribute_id.id,
                            {
                                "required": value.attribute_line_id.required,
                                "value_ids": [],
                            },
                        )
                        values_without_variant[value.attribute_id.id][
                            "value_ids"
                        ].append(value.product_attribute_value_id.id)
        return values_without_variant
