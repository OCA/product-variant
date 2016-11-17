# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        """Create possible product variants not yet created."""
        product_obj = self.env['product.product']
        lines_without_product = self.order_line.filtered(
            lambda x: not x.product_id and x.product_tmpl_id)

        for line in lines_without_product:

            product = product_obj._product_find(
                line.product_tmpl_id, line.product_attribute_ids)
            if not product:
                product = product_obj.create({
                    'product_tmpl_id': line.product_tmpl_id.id,
                    'attribute_value_ids':
                        [(6, 0,
                          line.product_attribute_ids.mapped('value_id').ids)]})
            line.write({'product_id': product.id})
        return super(PurchaseOrder, self).button_confirm()
