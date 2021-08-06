# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductVariantAttributeValueAction(models.TransientModel):
    _name = "variant.attribute.value.action"
    _description = "Wizard action to do on variant attribute value"
    _order = "attribute_id"

    product_attribute_value_id = fields.Many2one(
        comodel_name="product.attribute.value", ondelete="cascade"
    )
    attribute_action = fields.Selection(
        selection="_selection_action", default="do_nothing", required=True,
    )
    attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        related="product_attribute_value_id.attribute_id",
        readonly=True,
        store=True,
        ondelete="cascade",
    )
    selectable_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_selectable_attribute_value_ids",
    )
    replaced_by_id = fields.Many2one(
        comodel_name="product.attribute.value",
        string="Replace with",
        domain="[('id', 'in', selectable_attribute_value_ids)]",
        ondelete="cascade",
    )

    def _selection_action(self):
        return [
            ("do_nothing", "Do Nothing"),
            ("replace", "Replace"),
            ("delete", "Delete"),
        ]

    @api.depends("attribute_action")
    def _compute_selectable_attribute_value_ids(self):
        for rec in self:
            attribute_ids = self.attribute_id.value_ids.ids
            rec.selectable_attribute_value_ids = [(6, 0, attribute_ids)]
