# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    price_display_variant_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        default=lambda self: self.env["product.pricelist.item"]._default_pricelist_id(),
        string="Base pricelist for product variants display price",
    )
