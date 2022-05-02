from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_sale_price = fields.Float('Variant Sale Price (extra prices included)', compute='_compute_variant_sale_price')

    def _compute_variant_sale_price(self):
        for product in self:
            product.variant_sale_price = product.price_extra + product.fix_price
