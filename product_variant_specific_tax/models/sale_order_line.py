# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            new_taxes = line.tax_id | line.product_id.additional_tax_ids
            if new_taxes != line.tax_id:
                line.tax_id = new_taxes
