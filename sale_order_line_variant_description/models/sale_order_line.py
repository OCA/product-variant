# Copyright 2015-17 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super(SaleOrderLine, self)._onchange_product_id_warning()
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description_sale:
                self.name = product.variant_description_sale
        return res
