# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    pricelist_base_price = fields.Float(
        compute="_compute_pricelist_base_price",
        digits="Product Price",
        string="Price (Base Pricelist)",
    )
    base_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        compute="_compute_base_pricelist_id",
    )

    @api.depends_context("company")
    def _compute_pricelist_base_price(self):
        pricelist = self.env.company.price_display_variant_pricelist_id
        for product in self:
            price = pricelist._get_product_price(product, 1)
            product.pricelist_base_price = price

    @api.depends_context("company")
    def _compute_base_pricelist_id(self):
        pricelist = self.env.company.price_display_variant_pricelist_id
        self.base_pricelist_id = pricelist
