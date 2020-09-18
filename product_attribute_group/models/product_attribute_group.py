# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeGroup(models.Model):
    _name = "product.attribute.group"
    _description = "Product Attribute Group"

    code = fields.Char()
    name = fields.Char(translate=True, required=True)
    attribute_value_ids = fields.One2many(
        "product.attribute.value", "group_id", "Attribute Value"
    )
    html_color = fields.Char()
