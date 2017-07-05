# -*- coding: utf-8 -*-
# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line', 'product.configurator']
    _name = 'purchase.order.line'

    product_id = fields.Many2one(required=False)

    def onchange_product_id(self):
        if self.env.context.get('product_id'):
            self.product_id = self.env.context.get('product_id')
        return super(PurchaseOrderLine, self).onchange_product_id()

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        """ Make use of PurchaseOrderLine onchange_product_id method """
        product = self.product_tmpl_id.with_context({
            'lang': self.order_id.partner_id.lang,
            'partner_id': self.order_id.partner_id.id,
        })._product_from_tmpl()
        return self.with_context({'product_id': product}).onchange_product_id()
