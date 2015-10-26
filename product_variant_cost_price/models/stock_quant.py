# -*- coding: utf-8 -*-
# (c) 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _get_variant_inventory_value(self):
        self.ensure_one()
        if self.product_id.cost_method == 'real':
            return self.cost * self.qty
        return self.product_id.standard_price * self.qty

    @api.multi
    @api.depends("product_id", "product_id.standard_price", "qty",
                 "product_id.product_tmpl_id.cost_method")
    def _compute_variant_inventory_value(self):
        for record in self:
            record.variant_inventory_value = record.with_context(
                force_company=record.company_id.id
                )._get_variant_inventory_value()

    variant_inventory_value = fields.Float(
        string="Inventory Value", store=True,
        compute="_compute_variant_inventory_value")
