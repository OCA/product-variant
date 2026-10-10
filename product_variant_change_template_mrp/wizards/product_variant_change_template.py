# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.fields import Command


class ProductVariantChangeTemplate(models.TransientModel):
    _inherit = "product.variant.change.template"

    @api.model
    def _get_bom_variant_elements(self, bom):
        """Parts of a bill of materials that can be restricted to variants."""
        return [bom.bom_line_ids, bom.operation_ids, bom.byproduct_ids]

    @api.model
    def _bom_element_applies(self, element, combination):
        """Whether a bill of materials element restricted to some variant
        values applies to a combination of attribute value ids, like
        ``_match_all_variant_values`` does with template attribute values.
        Attributes that do not create variants are not part of a combination
        and are ignored."""
        values = element.bom_product_template_attribute_value_ids.filtered(
            lambda v: v.attribute_id.create_variant != "no_variant"
        )
        for attribute in values.attribute_id:
            allowed = values.filtered(lambda v, a=attribute: v.attribute_id == a)
            if not combination & set(allowed.product_attribute_value_id.ids):
                return False
        return True

    def _narrow_record_to_variant(self, record, variant, values, plan, reuse=False):
        if record._name != "mrp.bom":
            return super()._narrow_record_to_variant(
                record, variant, values, plan, reuse=reuse
            )
        for elements in self._get_bom_variant_elements(record):
            if elements.bom_product_template_attribute_value_ids.filtered(
                lambda v: v.attribute_id.create_variant == "no_variant"
            ):
                raise UserError(
                    _(
                        "%(bom)s applies some of its elements depending on "
                        "attributes that do not create variants, which the bill "
                        "of materials of a single variant cannot express.",
                        bom=record.display_name,
                    )
                )
        combination = plan["source_combinations"][variant]
        # The original is never rewritten: stock moves of manufacturing orders
        # and kits point to its lines.
        bom = record.copy()
        for elements in self._get_bom_variant_elements(bom):
            restricted = elements.filtered("bom_product_template_attribute_value_ids")
            applying = restricted.filtered(
                lambda e: self._bom_element_applies(e, combination)
            )
            (restricted - applying).unlink()
            applying.bom_product_template_attribute_value_ids = [Command.clear()]
        bom.write(values)
        if reuse:
            record.active = False
        return bom

    def _clean_source_configuration(self, plan):
        """Values removed from a source would silently vanish from the variant
        restrictions of its bills of materials, making the elements restricted
        to them apply to every remaining variant. Replace those bills of
        materials with a version without the elements no remaining variant
        uses."""
        for source, removals in plan["source_removals"].items():
            removed = set().union(*removals.values())
            if not removed:
                continue
            remaining = [
                self._get_combination(v)
                for v in source.with_context(active_test=False).product_variant_ids
            ]
            boms = (
                self.env["mrp.bom"]
                .sudo()
                .search(
                    [("product_tmpl_id", "=", source.id), ("product_id", "=", False)]
                )
            )
            for bom in boms:
                if not self._get_dead_bom_elements(bom, removed, remaining):
                    continue
                new_bom = bom.copy()
                for elements in self._get_dead_bom_elements(
                    new_bom, removed, remaining
                ):
                    elements.unlink()
                bom.active = False
        return super()._clean_source_configuration(plan)

    def _get_dead_bom_elements(self, bom, removed, remaining):
        dead = []
        for elements in self._get_bom_variant_elements(bom):
            affected = elements.filtered(
                lambda e: set(
                    e.bom_product_template_attribute_value_ids.product_attribute_value_id.ids
                )
                & removed
            )
            unused = affected.filtered(
                lambda e: not any(
                    self._bom_element_applies(e, combination)
                    for combination in remaining
                )
            )
            if unused:
                dead.append(unused)
        return dead
