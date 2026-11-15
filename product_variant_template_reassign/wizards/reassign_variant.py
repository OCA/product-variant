# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from markupsafe import Markup
from openupgradelib.openupgrade_merge_records import merge_records

from odoo import api, fields, models
from odoo.exceptions import UserError


class ReassignVariant(models.TransientModel):
    _name = "reassign.variant"
    _description = "Reassign variant template"

    origin_product_template_id = fields.Many2one(comodel_name="product.template")
    allowed_target_product_template_ids = fields.Many2many(
        comodel_name="product.template",
        compute="_compute_allowed_target_product_template_ids",
    )
    target_product_template_id = fields.Many2one(
        comodel_name="product.template",
        domain="[('id', 'in', allowed_target_product_template_ids)]",
    )
    allowed_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_allowed_attribute_value_ids",
    )
    attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        domain="[('id', 'in', allowed_attribute_value_ids)]",
        compute="_compute_attribute_value_ids",
        readonly=False,
        store=True,
    )

    @api.model
    def default_get(self, fields_list):
        product_template = self.env["product.template"].browse(
            self.env.context.get("active_id", 0)
        )
        if not self.env["product.template"].has_access("create"):
            raise UserError(
                self.env._(
                    "Only users with permissions to create products can reassign "
                    "variants"
                )
            )
        if product_template and product_template.product_variant_count != 1:
            raise UserError(self.env._("You can only reassign unique variant products"))
        res = super().default_get(fields_list)
        if product_template:
            res["origin_product_template_id"] = product_template.id
        return res

    @api.depends("origin_product_template_id")
    def _compute_allowed_target_product_template_ids(self):
        self.allowed_target_product_template_ids = False
        for wiz in self.filtered("origin_product_template_id"):
            wiz.allowed_target_product_template_ids = self.env[
                "product.template"
            ].search(
                [
                    ("type", "=", wiz.origin_product_template_id.type),
                    (
                        "is_storable",
                        "=",
                        wiz.origin_product_template_id.is_storable,
                    ),
                    ("uom_id", "=", wiz.origin_product_template_id.uom_id.id),
                    ("id", "!=", wiz.origin_product_template_id.id),
                    ("attribute_line_ids", "!=", False),
                ]
            )

    @api.depends("target_product_template_id")
    def _compute_allowed_attribute_value_ids(self):
        self.allowed_attribute_value_ids = False
        for wiz in self.filtered("target_product_template_id"):
            wiz.allowed_attribute_value_ids = (
                self.env["product.attribute.value"].search(
                    [
                        (
                            "attribute_id",
                            "in",
                            wiz.target_product_template_id.attribute_line_ids.attribute_id.ids,
                        ),
                        ("attribute_id.create_variant", "=", "always"),
                    ]
                )
                - wiz.target_product_template_id.attribute_line_ids.value_ids
            )

    @api.depends("target_product_template_id")
    def _compute_attribute_value_ids(self):
        """Whenever the target changes we must wipe the attribute values"""
        self.attribute_value_ids = False

    def _get_field_spec(self) -> dict:
        """Keep the values from the original variant using merge_records.
        See ``_adjust_merged_values_orm`` in
        ``openupgradelib/openupgrade_merge_records.py``.
        """
        field_spec_map = {
            "char": "first_from_origin",
            "html": "first_from_origin",
            "text": "first_from_origin",
            "float": "first_from_origin",
            "integer": "first_from_origin",
            "monetary": "first_from_origin",
            "binary": "first_from_origin",
            "date": "first_from_origin",
            "datetime": "first_from_origin",
            "many2one": "first_from_origin",
            "many2many": "first_from_origin",
            "one2many": "first_from_origin",
            "reference": "first_from_origin",
            "selection": "first_from_origin",
            "serialized": "first_from_origin",
            "jsonb": "first_from_origin",
            "boolean": "first_from_origin",
        }
        fields = [
            self.env["product.product"]._fields[f]
            for f in self.env["product.product"]._fields
        ]
        banned_fields = ["product_tmpl_id", "id"]
        res = {
            field.name: field_spec_map.get(field.type)
            for field in fields
            if field_spec_map.get(field.type) and field.name not in banned_fields
        }
        return res

    def _preprocess_data(self):
        """Called before the merge. Some of origin variant data might be problematic.
        Override to deal with other issues"""
        variant = self.origin_product_template_id.product_variant_id
        self.origin_product_template_id.attribute_line_ids.filtered(
            lambda x: x.attribute_id.create_variant != "no_variant"
        ).unlink()
        # Take a snapshot of the original variant data before the merge
        original_values = variant.read()[0]
        return original_values

    def _clear_duplicated_attributes(self):
        """No variant attributes are merged into the resulting template. We need to
        get rid of duplicates"""
        attribute_lines = self.target_product_template_id.attribute_line_ids.filtered(
            lambda x: x.attribute_id.create_variant == "no_variant"
        )
        dupes_to_delete = self.env["product.template.attribute.line"]
        for attribute in attribute_lines.attribute_id:
            att_lines = attribute_lines.filtered(
                lambda x, attribute=attribute: x.attribute_id == attribute
            )
            # There's only one...
            if len(att_lines) == 1:
                continue
            definitive_line = att_lines[0]
            definitive_line.value_ids = att_lines.value_ids
            dupes_to_delete += att_lines - definitive_line
        dupes_to_delete.unlink()

    def _postprocess_data(self, new_variant, original_data):
        """Called after the merge. Some info might not be merged correctly. Override
        here to reset the original data"""
        # We need to reload the ORM cache to get rid of old stuff
        self.env.invalidate_all()
        # There can be special cases like list_price where the values are handled
        # by the ORM as the column is delegated from the product template.
        fields_to_update = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("product_variant_template_reassign.keep_fields")
            or ""
        )
        vals_to_keep = {
            field: original_data[field]
            for field in fields_to_update.split(",")
            if field in original_data
        }
        # Ensure that we keep the image
        vals_to_keep["image_variant_1920"] = (
            vals_to_keep.get("image_variant_1920")
            or original_data.get("image_variant_1920")
            or original_data.get("image_1920")
        )
        new_variant.update(vals_to_keep)
        self._clear_duplicated_attributes()

    def reassign(self):
        """No way back! The potential new variant from the selected attributes is
        merged with the origin variant"""
        # 1. Create variant
        existing_variants = self.target_product_template_id.product_variant_ids
        for attribute_value in self.attribute_value_ids:
            self.target_product_template_id.attribute_line_ids.filtered(
                lambda x, attribute_value=attribute_value: x.attribute_id
                == attribute_value.attribute_id
            ).value_ids += attribute_value
        new_variant = (
            self.target_product_template_id.product_variant_ids - existing_variants
        )
        if not new_variant:
            raise UserError(
                self.env._(
                    "The selected attributes didn't generate a variant in the "
                    "target template"
                )
            )
        try:
            new_variant.ensure_one()
        except ValueError:
            raise UserError(
                self.env._(
                    "The selected attributes generate more than one variant. "
                    "Refine your configuration"
                )
            ) from None
        # Pre-process potential problematic stuff with the variant
        original_values = self._preprocess_data()
        # 2. Merge existing variant into the new one. Do it with SQL to avoid ORM locks
        merge_records(
            self.env,
            "product.product",
            self.origin_product_template_id.product_variant_id.ids,
            new_variant.id,
            field_spec=self._get_field_spec(),
            method="sql",
        )
        # 3. Merge origin template into the target template. Do it with SQL to avoid ORM
        # locks.
        merge_records(
            self.env,
            "product.template",
            self.origin_product_template_id.ids,
            self.target_product_template_id.id,
            method="sql",
        )
        self._postprocess_data(new_variant, original_values)
        body = Markup(
            '<a href="#" data-oe-model="product.product" data-oe-id="%(id)s">'
            "%(name)s</a> %(message)s"
        ) % {
            "id": new_variant.id,
            "name": new_variant.display_name,
            "message": self.env._("reassigned to this template"),
        }
        self.target_product_template_id.message_post(body=body)
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "view_mode": "form",
            "res_id": self.target_product_template_id.id,
        }
