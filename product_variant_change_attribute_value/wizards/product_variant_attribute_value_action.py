# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductVariantAttributeValueAction(models.TransientModel):
    _name = "variant.attribute.value.action"
    _description = "Wizard action to do on variant attribute value"

    def _get_attribute_action_list(self):
        return [
            ("delete", "Delete"),
            ("replace", "Replace"),
            ("do_nothing", "Do Nothing"),
        ]

    product_attribute_value_id = fields.Many2one("product.attribute.value",)
    attribute_action = fields.Selection(
        selection="_get_attribute_action_list", default="do_nothing", required=True,
    )
    attribute_id = fields.Many2one(
        "product.attribute",
        related="product_attribute_value_id.attribute_id",
        readonly=True,
    )
    selectable_attribute_value_ids = fields.Many2many(
        "product.attribute.value", compute="_compute_selectable_attribute_value_ids"
    )
    replaced_by_id = fields.Many2one(
        "product.attribute.value",
        string="Replace with",
        domain="[('id', 'in', selectable_attribute_value_ids)]",
    )

    @api.depends("attribute_action")
    def _compute_selectable_attribute_value_ids(self):
        for rec in self:
            attribute_ids = self.attribute_id.value_ids.ids
            rec.selectable_attribute_value_ids = [(6, 0, attribute_ids)]
