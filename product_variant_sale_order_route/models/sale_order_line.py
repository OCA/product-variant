# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id:
            self.update(
                {'route_id': self.product_id.sale_order_line_route_id.id}
            )
        return res
