# -*- coding: utf-8 -*-
# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        """Create possible product variants not yet created."""
        lines_without_product = self.order_line.filtered(
            lambda x: not x.product_id and x.product_tmpl_id
        )
        for line in lines_without_product:
            line.create_variant_if_needed()
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def copy(self, default=None):
        """Change date_planned for lines without product after calling super"""
        new_po = super(PurchaseOrder, self).copy(default=default)
        for line in new_po.order_line.filtered(lambda x: not x.product_id):
            product = line.product_tmpl_id._product_from_tmpl()
            seller = product._select_seller(
                partner_id=line.partner_id, quantity=line.product_qty,
                date=(line.order_id.date_order or '')[:10] or None,
                uom_id=line.product_uom,
            )
            line.date_planned = line._get_date_planned(seller)
        return new_po


class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line', 'product.configurator']
    _name = 'purchase.order.line'

    product_id = fields.Many2one(required=False)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id_configurator(self):
        """ Make use of PurchaseOrderLine onchange_product_id method with
        a virtual product created on the fly.
        """
        self.product_id = self.product_tmpl_id._product_from_tmpl()
        self.onchange_product_id()
        self.product_id = False
        # HACK: With NewId, making `with_context` loses temp values, so we
        # need to recreate these operations
        product_lang = self.product_tmpl_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase
        return super(
            PurchaseOrderLine, self,
        )._onchange_product_tmpl_id_configurator()

    @api.model
    def create(self, vals):
        """Create variant before calling super when the purchase order is
        confirmed, as it creates associated stock moves.
        """
        if 'order_id' not in vals or vals.get('product_id'):
            return super(PurchaseOrderLine, self).create(vals)
        order = self.env['purchase.order'].browse(vals['order_id'])
        if order.state == 'purchase':
            line = self.new(vals)
            product = line.create_variant_if_needed()
            vals['product_id'] = product.id
        return super(PurchaseOrderLine, self).create(vals)
