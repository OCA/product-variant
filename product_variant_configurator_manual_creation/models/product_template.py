# Copyright 2022 ForgeFlow S.L. <https://forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_pending_variants = fields.Boolean(
        string="Has pending variants?",
        compute="_compute_has_pending_variants",
    )

    def _possible_pending_variants_calculation(self):
        # If the product has not been created yet,
        # it is useless to check for pending variants.
        if isinstance(
            self.id,
            models.NewId,
        ):
            return False

        # Use the maximum number of combinations to avoid infinite processing
        # this value is also set in self._create_variant_ids() in `product` module
        possible_combination_downcounter = 1000

        product_template_attribute_values_per_line = [
            ptal.product_template_value_ids._only_active()
            for ptal in self.valid_product_template_attribute_line_ids
        ]

        # iterate over lines and check whether there is any newId
        for line in product_template_attribute_values_per_line:
            for product_template_attribute_value in line:
                if isinstance(
                    product_template_attribute_value.id,
                    models.NewId,
                ) or isinstance(
                    product_template_attribute_value.attribute_id.id, models.NewId
                ):
                    return False

            # If line is empty (no configurable attribute values)
            # remove it from the list so _cartesian_product still works
            if not line:
                product_template_attribute_values_per_line.remove(line)

        cartesian_generator = self._cartesian_product(
            product_template_attribute_values_per_line, None
        )

        # next() the generator until it's exhausted or hits
        # "possible_combination_downcounter" combinations
        while next(cartesian_generator, None):
            possible_combination_downcounter -= 1
            if possible_combination_downcounter == 0:
                return False

        return True

    @api.depends(
        "product_variant_ids",
        "attribute_line_ids",
        "attribute_line_ids.attribute_id",
        "attribute_line_ids.value_ids",
    )
    def _compute_has_pending_variants(self):
        for rec in self:
            if not rec._possible_pending_variants_calculation():
                # Disable wizard as it will be impossible
                # to compute all values without variant
                rec.has_pending_variants = False
                continue

            # proceed with the accurate calculation
            rec.has_pending_variants = bool(self._get_values_without_variant())

    def _get_values_without_variant(self):
        lines_without_no_variants = (
            self.valid_product_template_attribute_line_ids._without_no_variant_attributes()
        )
        all_variants = self.product_variant_ids.sorted(
            lambda p: (p.active, p.id and -p.id or False)
        )
        all_combinations = itertools.product(
            *[
                ptal.product_template_value_ids._only_active()
                for ptal in lines_without_no_variants
            ]
        )
        existing_variants = {
            variant.product_template_attribute_value_ids: variant
            for variant in all_variants
        }
        values_without_variant = {}
        for combination_tuple in all_combinations:
            combination = self.env["product.template.attribute.value"].concat(
                *combination_tuple
            )
            is_combination_possible = self._is_combination_possible_by_config(
                combination, ignore_no_variant=True
            )
            if not is_combination_possible:
                continue
            if combination not in existing_variants:
                for value in combination:
                    if isinstance(value.attribute_id.id, models.NewId) or isinstance(
                        value.product_attribute_value_id.id, models.NewId
                    ):
                        continue
                    values_without_variant.setdefault(
                        value.attribute_id.id,
                        {
                            "required": value.attribute_line_id.required,
                            "value_ids": [],
                        },
                    )
                    values_without_variant[value.attribute_id.id]["value_ids"].append(
                        value.product_attribute_value_id.id
                    )
        return values_without_variant
