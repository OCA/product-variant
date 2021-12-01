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
        # Use SQL because loading all `value_ids` from each related attribute
        # is veeery slow. We don't care about permission at this point.
        query = """
            SELECT
                attribute_id,array_agg(id)
            FROM
                product_attribute_value
            WHERE
                attribute_id IN %(ids)s
            GROUP BY
                attribute_id
        """
        ids = tuple(self.mapped("attribute_id").ids)
        if not ids:
            self.update({"selectable_attribute_value_ids": False})
            return
        self.env["product.attribute.value"].flush(["attribute_id"])
        self.env.cr.execute(query, dict(ids=ids))
        values_by_attr = dict(self.env.cr.fetchall())
        for rec in self:
            rec.selectable_attribute_value_ids = [
                (6, 0, values_by_attr.get(rec.attribute_id.id, []))
            ]
