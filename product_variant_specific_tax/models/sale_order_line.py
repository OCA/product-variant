# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            fpos = line.order_id.fiscal_position_id or \
                line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.additional_tax_ids.filtered(
                lambda r:
                not line.company_id or r.company_id == line.company_id
            )
            fpos_taxes = fpos.map_tax(
                taxes, line.product_id, line.order_id.partner_shipping_id
            ) if fpos else taxes

            line.tax_id |= fpos_taxes
