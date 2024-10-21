import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WizardProductVariantChangeTemplate(models.TransientModel):

    _name = "wizard.product.variant.change.template"

    _description = "Wizard to change template in product variant"

    current_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Current Product",
        required=True,
        readonly=True,
    )
    current_template_id = fields.Many2one(
        related="current_product_id.product_tmpl_id",
    )
    destination_template_id = fields.Many2one(
        comodel_name="product.template", string="Destination Template", required=True
    )
    available_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="rel_wizard_change_template_value_available",
        column1="wizard_line_id",
        column2="value_id",
        string="Available Attributes",
        readonly=True,
    )
    selected_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="rel_wizard_change_template_value_selected",
        column1="wizard_line_id",
        column2="value_id",
        string="Attributes to apply",
    )
    require_attribute_selection = fields.Boolean(
        compute="_compute_require_attribute_selection"
    )
    already_exist_variant_ids = fields.Many2many(
        comodel_name="product.product", compute="_compute_already_exist_variant"
    )
    is_different_uom = fields.Boolean(compute="_compute_different_uom")
    current_uom_id = fields.Many2one(
        related="current_template_id.uom_id", string="Current UoM"
    )
    destination_uom_id = fields.Many2one(
        related="destination_template_id.uom_id", string="Destination UoM"
    )

    @api.depends("destination_template_id", "current_template_id")
    def _compute_different_uom(self):
        for rec in self:
            different = (
                rec.destination_template_id.uom_id != rec.current_template_id.uom_id
            )
            rec.is_different_uom = rec.destination_template_id and different or False

    @api.depends("destination_template_id", "selected_value_ids")
    def _compute_already_exist_variant(self):
        for rec in self:
            already_exist_product = self.env["product.product"].search(
                [
                    ("product_tmpl_id", "=", rec.destination_template_id.id),
                    (
                        "product_template_attribute_value_ids.product_attribute_value_id",
                        "=",
                        self.selected_value_ids.ids,
                    ),
                ]
            )
            already_exist_product = already_exist_product.filtered(
                lambda x: sorted(
                    x.mapped(
                        "product_template_attribute_value_ids.product_attribute_value_id"
                    ).ids
                )
                == sorted(self.selected_value_ids.ids)
            )
            self.already_exist_variant_ids = already_exist_product.ids or [
                Command.clear()
            ]

    @api.depends("destination_template_id")
    def _compute_require_attribute_selection(self):
        for rec in self:
            rec.require_attribute_selection = bool(
                rec.destination_template_id.attribute_line_ids.filtered(
                    lambda x: x.value_ids
                )
            )

    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        values.update(
            {
                "current_product_id": self.env.context.get("active_id"),
            }
        )
        return values

    @api.onchange("destination_template_id", "selected_value_ids")
    def _onchange_attributes(self):
        all_values = self.destination_template_id.attribute_line_ids.mapped("value_ids")
        attributes_selected = self.selected_value_ids.mapped("attribute_id")
        available_values = all_values.filtered(
            lambda x: x.id not in self.selected_value_ids.ids
        )
        available_values = available_values.filtered(
            lambda x: x.attribute_id.id not in attributes_selected.ids
        )
        self.available_value_ids = available_values.ids or [Command.clear()]

    def _check_attributes_required(self):
        attributes_required = self.destination_template_id.attribute_line_ids.filtered(
            lambda x: x.required
        ).mapped("attribute_id")
        attributed_selected = self.selected_value_ids.mapped("attribute_id")
        for attribute in attributes_required:
            if attribute.id not in attributed_selected.ids:
                raise UserError(
                    _(
                        "Required attribute %s is not in selected attributes, please check"
                    )
                    % attribute.display_name
                )

    def _handle_price_list_item_change(self):
        if self.current_template_id != self.destination_template_id:
            if self.current_template_id.product_variant_count == 1:
                price_list_related = self.env["product.pricelist.item"].search(
                    [
                        ("product_tmpl_id", "=", self.current_template_id.id),
                        ("applied_on", "=", "1_product"),
                    ]
                )
                if price_list_related:
                    price_list_related.write(
                        {
                            "applied_on": "0_product_variant",
                            "product_tmpl_id": False,
                            "product_id": self.current_product_id.id,
                        }
                    )

    def _handle_supplier_info_change(self):
        if self.current_template_id != self.destination_template_id:
            if self.current_template_id.product_variant_count == 1:
                for supplier_info in self.current_template_id.variant_seller_ids:
                    # CHECKME: Is better to write in current data or copy?
                    supplier_info.copy(
                        {
                            "product_tmpl_id": self.destination_template_id.id,
                            "product_id": self.current_product_id.id,
                        }
                    )

    def action_change_template(self):
        if self.is_different_uom:
            raise UserError(
                _(
                    "You can't use a destination template "
                    "with different UoM of original template"
                )
            )
        if self.already_exist_variant_ids:
            raise UserError(
                _(
                    "You can't assign this combination, a "
                    "variant already exists in template selected"
                )
            )
        self._check_attributes_required()
        current_attribute_value = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", self.destination_template_id.id),
                ("product_attribute_value_id", "in", self.selected_value_ids.ids),
            ]
        )
        current_template = self.current_template_id
        current_lst_price = self.current_product_id.lst_price
        self._handle_price_list_item_change()
        self._handle_supplier_info_change()
        self.current_product_id.write(
            {
                "product_tmpl_id": self.destination_template_id.id,
                "product_template_attribute_value_ids": [Command.clear()]
                + [Command.link(value.id) for value in current_attribute_value],
            }
        )
        self.current_product_id.write(
            {
                "lst_price": current_lst_price,
            }
        )
        self.current_product_id.invalidate_model(["product_tmpl_id"])
        current_template.invalidate_model(["product_variant_ids"])
        if len(current_template.product_variant_ids) == 0:
            current_template.write(
                {
                    "active": False,
                }
            )
        return {"type": "ir.actions.act_window_close"}
