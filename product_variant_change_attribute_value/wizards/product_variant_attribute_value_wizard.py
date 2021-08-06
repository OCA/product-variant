# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class VariantAttributeValueWizard(models.TransientModel):
    _name = "variant.attribute.value.wizard"
    _description = "Wizard to change attriubtes on product variants"

    product_ids = fields.Many2many(comodel_name="product.product")
    product_variant_count = fields.Integer(compute="_compute_count")
    product_template_count = fields.Integer(compute="_compute_count")
    attributes_action_ids = fields.Many2many(
        comodel_name="variant.attribute.value.action",
        relation="variant_attribute_wizard_attribute_action_rel",
        compute="_compute_attributes_action_ids",
        readonly=False,
        store=True,
    )

    @api.depends("product_ids")
    def _compute_attributes_action_ids(self):
        for rec in self:
            ptavs = rec.product_ids.product_template_attribute_value_ids
            rec.attributes_action_ids = [
                (
                    0,
                    0,
                    {
                        "product_attribute_value_id": x.id,
                        "attribute_id": x.attribute_id,
                        "attribute_action": "do_nothing",
                    },
                )
                for x in ptavs.product_attribute_value_id
            ]

    @api.depends("product_ids")
    def _compute_count(self):
        for record in self:
            record.product_variant_count = len(record.product_ids)
            record.product_template_count = len(
                record.product_ids.mapped("product_tmpl_id")
            )

    def action_apply(self):
        for product in self.product_ids:
            self._action_apply(product)

    def _is_attribute_value_being_used(self, variant_id, attribute_value):
        """Check if attribute value is still used by a variant."""
        existing_variants = self.env["product.product"].search(
            [
                ("id", "!=", variant_id.id),
                ("product_tmpl_id", "=", variant_id.product_tmpl_id.id),
            ],
        )
        existing_attributes = existing_variants.mapped(
            "product_template_attribute_value_ids.product_attribute_value_id"
        )
        return attribute_value in existing_attributes

    def _action_apply(self, product):
        """Update a variant with all the actions set by the user in the wizard."""
        pav_ids = product.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id"
        )
        for value_action in self.attributes_action_ids:
            action = value_action.attribute_action
            if action == "do_nothing":
                continue
            pav = value_action.product_attribute_value_id
            if pav not in pav_ids:
                continue
            ptav_ids = product.product_template_attribute_value_ids.filtered(
                lambda r: r.product_attribute_value_id != pav
            )
            if action == "delete":
                # nothing to do because `_cleanup_attribute_value` will take care
                pass
            elif action == "replace":
                if not value_action.replaced_by_id:
                    continue
                tpl_attr_value = self._handle_replace(
                    product, value_action.replaced_by_id
                )
                ptav_ids |= tpl_attr_value

            # Update the values set on the product variant
            product.product_template_attribute_value_ids = ptav_ids
            # Remove the changed value from the template attribute line if needed
            if not self._is_attribute_value_being_used(product, pav):
                self._cleanup_attribute_value(product, pav)

    def _handle_replace(self, product, pav_replacement):
        TplAttrLine = self.env["product.template.attribute.line"]
        TplAttrValue = self.env["product.template.attribute.value"]
        template = product.product_tmpl_id
        # Find corresponding attribute line on template or create it
        attr = pav_replacement.attribute_id
        tpl_attr_line = template.attribute_line_ids.filtered(
            lambda l: l.attribute_id == attr
        )
        if not tpl_attr_line:
            tpl_attr_line = TplAttrLine.create(
                {
                    "product_tmpl_id": template.id,
                    "attribute_id": attr.id,
                    "value_ids": [(6, False, [pav_replacement.id])],
                }
            )
        # Ensure the value exists in this attribute line.
        # The context key 'update_product_template_attribute_values' avoids
        # to create/unlink variants when values are updated on the template
        # attribute line.
        tpl_attr_line.with_context(
            update_product_template_attribute_values=False
        ).write({"value_ids": [(4, pav_replacement.id)]})
        # Get (or create if needed) the 'product.template.attribute.value'
        tpl_attr_value = TplAttrValue.search(
            [
                ("attribute_line_id", "=", tpl_attr_line.id),
                ("product_attribute_value_id", "=", pav_replacement.id),
            ]
        )
        if not tpl_attr_value:
            tpl_attr_value = TplAttrValue.create(
                {
                    "attribute_line_id": tpl_attr_line.id,
                    "product_attribute_value_id": pav_replacement.id,
                }
            )
        return tpl_attr_value

    def _cleanup_attribute_value(self, product, pav):
        TplAttrValue = self.env["product.template.attribute.value"]
        template = product.product_tmpl_id
        tpl_attr_line = template.attribute_line_ids.filtered(
            lambda l: l.attribute_id == pav.attribute_id
        )
        tpl_attr_line.with_context(
            update_product_template_attribute_values=False
        ).write({"value_ids": [(3, pav.id)]})
        tpl_attr_value = TplAttrValue.search(
            [
                ("attribute_line_id", "=", tpl_attr_line.id),
                ("product_attribute_value_id", "=", pav.id),
            ]
        )
        if tpl_attr_value:
            tpl_attr_value.unlink()