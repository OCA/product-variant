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
        valid_attr_lines = self.valid_product_template_attribute_line_ids
        lines_without_no_variants = valid_attr_lines._without_no_variant_attributes()
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
            all_combinations = rec._get_all_variant_combinations()
            existing_variants = rec._get_existing_variants()

            for combination_tuple in all_combinations:
                combination = rec.env["product.template.attribute.value"].concat(
                    *combination_tuple
                )

                # Check against existing variants (fast) before exclusions (slow)
                if combination not in existing_variants:
                    if rec._is_combination_possible_by_config(
                        combination, ignore_no_variant=True
                    ):
                        for value in combination:
                            if rec._can_add_variant(value):
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
            combination = self.env["product.template.attribute.value"].concat(
                *combination_tuple
            )

            if combination in existing_variants:
                continue

            # Check exclusions only if it doesn't already exist
            if not self._is_combination_possible_by_config(
                combination, ignore_no_variant=True
            ):
                continue

            for value in combination:
                if self._can_add_variant(value):
                    attr_id = value.attribute_id.id
                    if attr_id not in values_without_variant:
                        values_without_variant[attr_id] = {
                            "required": value.attribute_line_id.required,
                            "value_ids": set(),
                        }
                    # Add to set (duplicates are automatically ignored)
                    values_without_variant[attr_id]["value_ids"].add(
                        value.product_attribute_value_id.id
                    )

        # Convert sets back to standard lists
        for _attr_id, data in values_without_variant.items():
            data["value_ids"] = list(data["value_ids"])

        return values_without_variant
