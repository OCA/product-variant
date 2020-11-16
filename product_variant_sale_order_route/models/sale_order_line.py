# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()

        for record in self:
            if record.product_id:
                record.update(
                    {'route_id': self.product_id.sale_order_line_route_id.id}
                )
        return res
