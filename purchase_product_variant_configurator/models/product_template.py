# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import time


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def _select_seller(self, partner_id=False, quantity=0.0,
                       date=time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                       uom_id=False):
        # this method is copied from the standard _select_seller on the
        # product.product model
        self.ensure_one()
        res = self.env['product.supplierinfo'].browse([])
        for seller in self.seller_ids:
            quantity_uom_seller = quantity
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_qty_obj(
                    uom_id, quantity_uom_seller, seller.product_uom)
            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.name not in [partner_id,
                                                  partner_id.parent_id]:
                continue
            if quantity_uom_seller < seller.qty:
                continue
            if seller.product_tmpl_id and seller.product_tmpl_id != self:
                continue

            res |= seller
            break
        return res
