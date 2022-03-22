# Copyright 2022 ForgeFlow S.L. <https://forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools
import json

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    pending_variants = fields.Char(
        string="Pending variants", compute="_compute_pending_variants"
    )
    has_pending_variants = fields.Boolean(
        string="Has pending variants?", compute="_compute_pending_variants",
    )

    @api.depends(
        "product_variant_ids",
        "attribute_line_ids",
        "attribute_line_ids.attribute_id",
        "attribute_line_ids.value_ids",
    )
    def _compute_pending_variants(self):
        for rec in self:
            lines_without_no_variants = (
                rec.valid_product_template_attribute_line_ids._without_no_variant_attributes()
            )
            all_variants = rec.product_variant_ids.sorted(
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
                is_combination_possible = rec._is_combination_possible_by_config(
                    combination, ignore_no_variant=True
                )
                if not is_combination_possible:
                    continue
                if combination not in existing_variants:
                    for value in combination:
                        if not isinstance(value.attribute_id.id, models.NewId):
                            values_without_variant.setdefault(
                                value.attribute_id.id,
                                {
                                    "required": value.attribute_line_id.required,
                                    "value_ids": [],
                                },
                            )
                            if not isinstance(
                                value.product_attribute_value_id.id, models.NewId
                            ):
                                values_without_variant[value.attribute_id.id][
                                    "value_ids"
                                ].append(value.product_attribute_value_id.id)
            rec.has_pending_variants = bool(values_without_variant)
            rec.pending_variants = json.dumps(values_without_variant)
